from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import InventoryItem, InventoryAlert, PurchaseOrder
from django.utils import timezone
from datetime import timedelta

@receiver(post_save, sender=InventoryItem)
def check_inventory_levels(sender, instance, **kwargs):
    if instance.current_stock < instance.minimum_stock:
        InventoryAlert.objects.create(
            item=instance,
            alert_type='LOW_STOCK',
            message=f"Low stock alert for {instance.name}. Current stock: {instance.current_stock}"
        )
    elif instance.current_stock > instance.minimum_stock * 3:
        InventoryAlert.objects.create(
            item=instance,
            alert_type='OVERSTOCK',
            message=f"Overstock alert for {instance.name}. Current stock: {instance.current_stock}"
        )

@receiver(post_save, sender=InventoryItem)
def check_restock(sender, instance, **kwargs):
    if instance.auto_restock and instance.current_stock < instance.restock_threshold:
        PurchaseOrder.objects.create(
            supplier=instance.supplier,
            inventory_item=instance,
            quantity=instance.restock_threshold * 2,  # Order double threshold
            unit_price=instance.unit_price,
            expected_delivery=timezone.now() + timedelta(days=instance.supplier.lead_time)
        ) 