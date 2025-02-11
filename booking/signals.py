from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking, Waitlist
from hotel.models import InventoryItem
from django.db import transaction
from django.db.models import F
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Booking)
def handle_waitlist_promotion(sender, instance, created, **kwargs):
    if instance.status == 'cancelled':
        with transaction.atomic():
            # Lock the waitlist entries for update
            next_waitlist = Waitlist.objects.select_for_update(
                skip_locked=True
            ).filter(
                room_type=instance.room_type,
                check_in=instance.check_in_date,
                check_out=instance.check_out_date
            ).order_by('created_at').first()
            
            if next_waitlist:
                try:
                    with transaction.atomic():
                        # Create new booking for waitlisted user
                        Booking.objects.create(
                            user=next_waitlist.user,
                            hotel=instance.hotel,
                            room_type=instance.room_type,
                            check_in_date=instance.check_in_date,
                            check_out_date=instance.check_out_date,
                            total=instance.total,
                            status='confirmed',
                            waitlist_position=1
                        )
                        # Update inventory
                        InventoryItem.objects.filter(
                            room_type=instance.room_type
                        ).update(current_stock=F('current_stock') - 1)
                        
                        next_waitlist.delete()
                        logger.info(f"Promoted waitlist entry {next_waitlist.id}")
                except Exception as e:
                    logger.error(f"Waitlist promotion failed: {str(e)}")
                    # Implement retry logic or admin notification 