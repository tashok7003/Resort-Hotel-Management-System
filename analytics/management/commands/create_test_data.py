from django.core.management.base import BaseCommand
from hotel.models import Hotel, Room, RoomType, RoomServiceRequest, RoomServiceFeedback
from booking.models import Booking, CancellationPolicy
from django.contrib.auth import get_user_model
from django.core.files import File
from django.conf import settings
import os
from django.utils import timezone
import random
from datetime import timedelta
from decimal import Decimal
from django.apps import apps

class Command(BaseCommand):
    help = 'Creates test data for analytics'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        
        # Create test user if doesn't exist
        user, created = User.objects.get_or_create(
            username='testuser',
            email='test@example.com',
            defaults={'password': 'testpass123'}
        )
        
        # Create test hotel
        hotel, created = Hotel.objects.get_or_create(
            name='Test Hotel',
            user=user,
            defaults={
                'address': 'Test Address',
                'mobile': '1234567890',
                'email': 'hotel@test.com',
                'status': 'Live',
                'description': 'Test hotel description',
                'image': 'hotel_gallery/default.jpg'
            }
        )
        
        # Create room types with prices
        room_types = [
            ('King', 300),
            ('Luxury', 200),
            ('Normal', 100),
            ('Economic', 50)
        ]
        
        for rt, price in room_types:
            # Create room type with price and number_of_beds
            room_type, created = RoomType.objects.get_or_create(
                hotel=hotel,
                type=rt,
                defaults={
                    'price': price,
                    'number_of_beds': 2
                }
            )
            
            # Create rooms for each type
            for i in range(5):  # 5 rooms per type
                Room.objects.get_or_create(
                    hotel=hotel,
                    room_type=room_type,
                    room_number=f'{rt[0]}{i+1}',
                    defaults={
                        'is_available': True,
                        'rid': f'room_{rt[0]}{i+1}'
                    }
                )
        
        # Create a default cancellation policy
        cancellation_policy, _ = CancellationPolicy.objects.get_or_create(
            name='Standard Policy',
            defaults={
                'hours_before_checkin': 24,
                'charge_percentage': Decimal('50.00'),
                'description': 'Standard cancellation policy'
            }
        )

        # Add test room service requests and feedback
        for room in Room.objects.all():
            # Create 2 service requests per room
            for _ in range(2):
                try:
                    # Create a booking first
                    base_price = room.room_type.price  # Get base price from room type
                    booking = Booking.objects.create(
                        user=user,
                        hotel=hotel,
                        room_type=room.room_type,
                        check_in_date=timezone.now().date(),
                        check_out_date=timezone.now().date() + timedelta(days=2),
                        total=base_price,
                        base_price=base_price,
                        seasonal_multiplier=Decimal('1.0'),
                        demand_multiplier=Decimal('1.0'),
                        group_discount=Decimal('0.0'),
                        cancellation_policy=cancellation_policy,
                        cancellation_fee=Decimal('0.0'),
                        status='confirmed',
                        is_group_booking=False,
                        group_size=1
                    )

                    # Save the booking first
                    booking.save()
                    
                    # Create service request
                    Booking = apps.get_model('booking', 'Booking')
                    RoomServiceRequest = apps.get_model('hotel', 'RoomServiceRequest')
                    RoomServiceFeedback = apps.get_model('hotel', 'RoomServiceFeedback')

                    service_request = RoomServiceRequest.objects.create(
                        booking_id=booking.id,  # Use booking_id instead of booking object
                        service_type=random.choice(['Food', 'Cleaning', 'Technical']),
                        description='Test service request',
                        priority=random.choice(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
                        status='COMPLETED',
                        room_number=room.room_number,
                        guest_name='Test Guest'
                    )
                    
                    # Create feedback
                    RoomServiceFeedback.objects.create(
                        service_request=service_request,
                        rating=random.randint(1, 5),
                        comment='Test feedback'
                    )

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating test data: {str(e)}'))
                    continue

        self.stdout.write(self.style.SUCCESS('Successfully created test data')) 