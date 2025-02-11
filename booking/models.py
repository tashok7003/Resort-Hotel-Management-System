from django.db import models
from hotel.models import Hotel, RoomType
from userauths.models import User
from decimal import Decimal

# Add these at the top of the file with other choices
PAYMENT_STATUS = (
    ("paid", "Paid"),
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("cancelled", "Cancelled"),
    ("initiated", 'Initiated'),
    ("failed", 'Failed'),
    ("refunding", 'Refunding'),
    ("refunded", 'Refunded'),
    ("unpaid", 'Unpaid'),
    ("expired", 'Expired'),
)

class CancellationPolicy(models.Model):
    name = models.CharField(max_length=200)
    hours_before_checkin = models.PositiveIntegerField()
    charge_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class BookingPackage(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    included_room_types = models.ManyToManyField(RoomType)
    additional_services = models.JSONField(default=dict)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    terms = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='booking_hotel')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='booking_room_type')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total = models.DecimalField(max_digits=12, decimal_places=2)
    is_group_booking = models.BooleanField(default=False)
    group_size = models.PositiveIntegerField(default=1)
    group_leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='group_leader_bookings')
    group_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    seasonal_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    demand_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    cancellation_policy = models.ForeignKey(CancellationPolicy, on_delete=models.SET_NULL, null=True)
    cancellation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    package = models.ForeignKey(BookingPackage, on_delete=models.SET_NULL, null=True, blank=True)
    waitlist_position = models.PositiveIntegerField(null=True, blank=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def calculate_total(self):
        dynamic_price = self.base_price * self.seasonal_multiplier * self.demand_multiplier
        discounted = dynamic_price - (dynamic_price * self.group_discount / 100)
        self.total = discounted * self.group_size
        self.save()

class Waitlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'room_type', 'check_in', 'check_out')

class GroupBooking(models.Model):
    booking = models.OneToOneField('Booking', on_delete=models.CASCADE)
    group_leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_groups')
    group_name = models.CharField(max_length=100)
    group_size = models.PositiveIntegerField()
    group_type = models.CharField(max_length=50, choices=[
        ('CORPORATE', 'Corporate'),
        ('FAMILY', 'Family'),
        ('TOUR', 'Tour Group'),
        ('OTHER', 'Other')
    ])
    special_requests = models.TextField(blank=True)
    discount_applied = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    PAYMENT_TYPE_CHOICES = [
        ('FULL', 'Full Payment'),
        ('SPLIT', 'Split Payment'),
        ('DEPOSIT', 'Deposit Required')
    ]
    
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES, default='FULL')
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_paid = models.BooleanField(default=False)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def calculate_discount(self):
        """Calculate discount based on group size"""
        if self.group_size >= 20:
            return 20  # 20% discount
        elif self.group_size >= 15:
            return 15
        elif self.group_size >= 10:
            return 10
        elif self.group_size >= 5:
            return 5
        return 0

    def calculate_deposit(self):
        """Calculate required deposit (30% of total)"""
        return self.booking.total * Decimal('0.3')
    
    def get_remaining_payment(self):
        """Get remaining amount to be paid"""
        return self.booking.total - self.total_paid

class GroupMember(models.Model):
    group_booking = models.ForeignKey(GroupBooking, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    is_checked_in = models.BooleanField(default=False)
    special_requirements = models.TextField(blank=True)
    room_preference = models.ForeignKey('hotel.RoomType', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name} - {self.group_booking.group_name}"

class GroupRoomAllocation(models.Model):
    group_booking = models.ForeignKey(GroupBooking, on_delete=models.CASCADE)
    member = models.ForeignKey(GroupMember, on_delete=models.CASCADE)
    room = models.ForeignKey('hotel.Room', on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    
    class Meta:
        unique_together = ('room', 'check_in_date')

class GroupPayment(models.Model):
    group_booking = models.ForeignKey(GroupBooking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100)
    paid_by = models.ForeignKey(GroupMember, on_delete=models.SET_NULL, null=True)
    is_deposit = models.BooleanField(default=False)

class GroupBookingReport(models.Model):
    group_booking = models.OneToOneField(GroupBooking, on_delete=models.CASCADE)
    total_rooms = models.IntegerField()
    total_members = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    average_stay_length = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
