from django.db import transaction
from django.core.exceptions import ValidationError

class RoomAllocationService:
    def __init__(self, group_booking):
        self.group_booking = group_booking
        
    def allocate_rooms(self):
        """Allocate rooms based on member preferences and availability"""
        with transaction.atomic():
            members = self.group_booking.groupmember_set.all()
            for member in members:
                available_room = self.find_available_room(member.room_preference)
                if not available_room:
                    raise ValidationError(f"No available rooms of type {member.room_preference}")
                
                GroupRoomAllocation.objects.create(
                    group_booking=self.group_booking,
                    member=member,
                    room=available_room,
                    check_in_date=self.group_booking.booking.check_in_date,
                    check_out_date=self.group_booking.booking.check_out_date
                )
                
    def find_available_room(self, room_type):
        """Find an available room of the specified type"""
        return Room.objects.filter(
            room_type=room_type,
            is_available=True
        ).exclude(
            grouproomallocation__check_in_date__lte=self.group_booking.booking.check_out_date,
            grouproomallocation__check_out_date__gte=self.group_booking.booking.check_in_date
        ).first()

class GroupPaymentService:
    def __init__(self, group_booking):
        self.group_booking = group_booking
        
    def process_deposit(self, amount, payment_method, transaction_id):
        """Process deposit payment"""
        if amount < self.group_booking.calculate_deposit():
            raise ValidationError("Deposit amount is insufficient")
            
        with transaction.atomic():
            GroupPayment.objects.create(
                group_booking=self.group_booking,
                amount=amount,
                payment_method=payment_method,
                transaction_id=transaction_id,
                is_deposit=True
            )
            self.group_booking.deposit_paid = True
            self.group_booking.total_paid += amount
            self.group_booking.save()
            
    def process_split_payment(self, member, amount, payment_method, transaction_id):
        """Process split payment from a group member"""
        with transaction.atomic():
            GroupPayment.objects.create(
                group_booking=self.group_booking,
                amount=amount,
                payment_method=payment_method,
                transaction_id=transaction_id,
                paid_by=member
            )
            self.group_booking.total_paid += amount
            if self.group_booking.total_paid >= self.group_booking.booking.total:
                self.group_booking.payment_status = 'paid'
            self.group_booking.save() 