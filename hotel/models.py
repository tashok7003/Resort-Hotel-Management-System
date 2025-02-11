from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.template.defaultfilters import escape
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from userauths.models import User

import shortuuid
from taggit.managers import TaggableManager
from datetime import datetime


ICON_TPYE = (
    ('Bootstap Icons', 'Bootstap Icons'),
    ('Fontawesome Icons', 'Fontawesome Icons'),
)

ROOM_TYPES = (
    ('King', 'King'),
    ('Luxury', 'Luxury'),
    ('Normal', 'Normal'),
    ('Economic', 'Economic'),
)


SERVICES_TYPES = (
    ('Food', 'Food'),
    ('Cleaning', 'Cleaning'),
    ('Technical', 'Technical'),
)

HOTEL_STATUS = (
    ("Draft", "Draft"),
    ("Disabled", "Disabled"),
    ("Rejected", "Rejected"),
    ("In Review", "In Review"),
    ("Live", "Live"),
)

GENDER = (
    ("Male", "Male"),
    ("Female", "Female"),
)


DISCOUNT_TYPE = (
    ("Percentage", "Percentage"),
    ("Flat Rate", "Flat Rate"),
)

PAYMENT_STATUS = (
    ("paid", "Paid"),
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("cancelled", "Cancelled"),
    ("initiated", 'Initiated'),
    ("failed", 'failed'),
    ("refunding", 'refunding'),
    ("refunded", 'refunded'),
    ("unpaid", 'unpaid'),
    ("expired", 'expired'),
)



NOTIFICATION_TYPE = (
    ("Booking Confirmed", "Booking Confirmed"),
    ("Booking Cancelled", "Booking Cancelled"),
)


RATING = (
    ( 1,  "★☆☆☆☆"),
    ( 2,  "★★☆☆☆"),
    ( 3,  "★★★☆☆"),
    ( 4,  "★★★★☆"),
    ( 5,  "★★★★★"),
)

class Hotel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = CKEditor5Field(config_name='extends', null=True, blank=True)
    image = models.FileField(upload_to="hotel_gallery")
    address = models.CharField(max_length=200)
    mobile = models.CharField(max_length=20)
    email = models.CharField(max_length=20)
    status = models.CharField(choices=HOTEL_STATUS, max_length=10, default="published", null=True, blank=True)

    tags = TaggableManager(blank=True)
    views = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False)
    hid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    slug = models.SlugField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.name) + "-" + str(uniqueid.lower())
            
        super(Hotel, self).save(*args, **kwargs) 

    def thumbnail(self):
        return mark_safe('<img src="%s" width="50" height="50" style="object-fit:cover; border-radius: 6px;" />' % (self.image.url))

    def hotel_gallery(self):
        return HotelGallery.objects.filter(hotel=self)
    
    def hotel_features(self):
        return HotelFeatures.objects.filter(hotel=self)

    def hotel_faqs(self):
        return HotelFAQs.objects.filter(hotel=self)

    def hotel_room_types(self):
        return RoomType.objects.filter(hotel=self)
    
    def average_rating(self):
        average_rating = Review.objects.filter(hotel=self, active=True).aggregate(avg_rating=models.Avg("rating"))
        return average_rating['avg_rating']
    
    def rating_count(self):
        rating_count = Review.objects.filter(hotel=self, active=True).count()
        return rating_count
    
class HotelGallery(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    image = models.FileField(upload_to="hotel_gallery")
    hgid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")

    def __str__(self):
        return str(self.hotel)

    class Meta:
        verbose_name_plural = "Hotel Gallery"
    

class HotelFeatures(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    icon_type = models.CharField(max_length=100, null=True, blank=True, choices=ICON_TPYE)
    icon = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    hfid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")

    def __str__(self):
        return str(self.hotel)
    
    class Meta:
        verbose_name_plural = "Hotel Features"
    
class HotelFAQs(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    question = models.CharField(max_length=1000)
    answer = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    hfid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")

    def __str__(self):
        return str(self.hotel)
    
    class Meta:
        verbose_name_plural = "Hotel FAQs"

class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    type = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    number_of_beds = models.PositiveIntegerField(default=0)
    room_capacity = models.PositiveIntegerField(default=0)
    rtid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    slug = models.SlugField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.hotel.name} - {self.price}"

    def rooms_count(self):
        return Room.objects.filter(room_type=self).count()
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.type) + "-" + str(uniqueid.lower())
            
        super(RoomType, self).save(*args, **kwargs) 
    

class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)
    rid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.room_type.type} -  Room {self.room_number}"

    def price(self):
        return self.room_type.price
    
    def number_of_beds(self):
        return self.room_type.number_of_beds
    


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotel_bookings')
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS, default="initiated")

    full_name = models.CharField(max_length=1000, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=1000, null=True, blank=True)
    
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True)
    room = models.ManyToManyField(Room)
    before_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_days = models.PositiveIntegerField(default=0)
    num_adults = models.PositiveIntegerField(default=1)
    num_children = models.PositiveIntegerField(default=0)
    checked_in = models.BooleanField(default=False)
    checked_out = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    checked_in_tracker = models.BooleanField(default=False, help_text="DO NOT CHECK THIS BOX")
    checked_out_tracker = models.BooleanField(default=False, help_text="DO NOT CHECK THIS BOX")
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    coupons = models.ManyToManyField("hotel.Coupon", blank=True)
    stripe_payment_intent = models.CharField(max_length=200,null=True, blank=True)
    success_id = ShortUUIDField(length=300, max_length=505, alphabet="abcdefghijklmnopqrstuvxyz1234567890")
    booking_id = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")


    def __str__(self):
        return f"{self.booking_id}"
    
    def rooms(self):
        return self.room.all().count()
    
class ActivityLog(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    guest_out = models.DateTimeField()
    guest_in = models.DateTimeField()
    description = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.booking)
    
class StaffOnDuty(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    staff_id = models.CharField(null=True, blank=True, max_length=100)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.staff_id)
    

class Coupon(models.Model):
    code = models.CharField(max_length=1000)
    type = models.CharField(max_length=100, choices=DISCOUNT_TYPE, default="Percentage")
    discount = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(100)])
    redemption = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    make_public = models.BooleanField(default=False)
    valid_from = models.DateField()
    valid_to = models.DateField()
    cid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")

    
    def __str__(self):
        return self.code
    
    class Meta:
        ordering =['-id']


class CouponUsers(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    
    full_name = models.CharField(max_length=1000)
    email = models.CharField(max_length=1000)
    mobile = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.coupon.code)
    
    class Meta:
        ordering =['-id']


class RoomServices(models.Model):
    booking = models.ForeignKey(Booking, null=True, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    service_type = models.CharField(max_length=20, choices=SERVICES_TYPES)
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)

    def str(self):
        return str(self.booking) + " " + str(self.room) + " " + str(self.service_type)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=100, default="new_order", choices=NOTIFICATION_TYPE)
    seen = models.BooleanField(default=False)
    nid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    date= models.DateField(auto_now_add=True)
    
    def __str__(self):
        return str(self.user.username)
    
    class Meta:
        ordering = ['-date']


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True)
    bid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    date= models.DateField(auto_now_add=True)
    
    def __str__(self):
        return str(self.user.username)
    
    class Meta:
        ordering = ['-date']



class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, blank=True, null=True, related_name="reviews")
    review = models.TextField(null=True, blank=True)
    reply = models.CharField(null=True, blank=True, max_length=1000)
    rating = models.IntegerField(choices=RATING, default=None)
    active = models.BooleanField(default=False)
    helpful = models.ManyToManyField(User, blank=True, related_name="helpful")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Reviews & Rating"
        ordering = ["-date"]
        
    def __str__(self):
        return f"{self.user.username} - {self.rating}"
        
class InventoryCategory(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='inventory_categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    reorder_threshold = models.PositiveIntegerField(default=10)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.name}"

class InventoryItem(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey('InventoryCategory', on_delete=models.CASCADE)
    current_stock = models.IntegerField()
    minimum_stock = models.IntegerField()
    reorder_point = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True)
    barcode = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=100)
    last_restocked = models.DateTimeField(auto_now=True)
    expiration_date = models.DateField(null=True, blank=True)
    
    def check_stock_level(self):
        if self.current_stock <= self.minimum_stock:
            InventoryAlert.objects.create(
                item=self,
                alert_type='low_stock',
                message=f'Low stock alert for {self.name}'
            )
        elif self.current_stock > self.reorder_point * 2:
            InventoryAlert.objects.create(
                item=self,
                alert_type='overstock',
                message=f'Overstock alert for {self.name}'
            )

class InventoryAlert(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=[
        ('low_stock', 'Low Stock'),
        ('expired', 'Expired Item'),
        ('overstock', 'Overstock'),
        ('reorder', 'Reorder Needed')
    ])
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

class InventoryTransaction(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=[
        ('addition', 'Stock Addition'),
        ('reduction', 'Stock Reduction'),
        ('adjustment', 'Stock Adjustment'),
        ('damaged', 'Damaged Stock'),
        ('expired', 'Expired Stock')
    ])
    quantity = models.IntegerField()
    transaction_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=100)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if self.transaction_type in ['addition', 'adjustment']:
            self.item.current_stock += self.quantity
        else:
            self.item.current_stock -= self.quantity
        self.item.save()
        self.item.check_stock_level()
        super().save(*args, **kwargs)

class Department(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.hotel.name} - {self.name}"

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    position = models.CharField(max_length=100)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    emergency_contact = models.CharField(max_length=100)
    skills = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"

    def get_used_leave_days(self, leave_type):
        year_start = timezone.now().replace(month=1, day=1)
        return LeaveRequest.objects.filter(
            staff=self,
            leave_type=leave_type,
            start_date__year=timezone.now().year,
            status='APPROVED'
        ).count()
    
    def get_performance_score(self):
        recent_metrics = PerformanceMetric.objects.filter(
            staff=self,
            date__gte=timezone.now() - timezone.timedelta(days=90)
        )
        if not recent_metrics.exists():
            return None
        return recent_metrics.aggregate(models.Avg('value'))['value__avg']
    
    def get_overtime_hours(self, month=None):
        query = OvertimeRecord.objects.filter(staff=self, approved=True)
        if month:
            query = query.filter(date__month=month)
        return query.aggregate(models.Sum('hours'))['hours__sum'] or 0

class Shift(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    notes = models.TextField(blank=True)
    
    def duration(self):
        return self.end_time - self.start_time

class Attendance(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    date = models.DateField()
    clock_in = models.TimeField()
    clock_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('LEAVE', 'On Leave')
    ])
    
    def hours_worked(self):
        if self.clock_out:
            return (datetime.combine(self.date, self.clock_out) - 
                   datetime.combine(self.date, self.clock_in))
        return None

class StaffTask(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High')
    ])
    
    def status(self):
        return "Completed" if self.completed else "Pending"

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    payment_terms = models.TextField()
    lead_time = models.PositiveIntegerField(help_text="Delivery lead time in days")
    minimum_order = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    performance_score = models.FloatField(default=0)
    active = models.BooleanField(default=True)
    last_order_date = models.DateTimeField(null=True, blank=True)
    total_orders = models.PositiveIntegerField(default=0)
    on_time_delivery_rate = models.FloatField(default=0)
    quality_rating = models.FloatField(default=0)
    
    def calculate_performance_score(self):
        # Weight factors for different metrics
        weights = {
            'rating': 0.3,
            'on_time_delivery': 0.4,
            'quality': 0.3
        }
        self.performance_score = (
            (self.rating * weights['rating']) +
            (self.on_time_delivery_rate * weights['on_time_delivery']) +
            (self.quality_rating * weights['quality'])
        )
        self.save()

class SupplierOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    expected_delivery = models.DateField()
    actual_delivery = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    quality_rating = models.FloatField(null=True, blank=True)
    
    def update_supplier_metrics(self):
        if self.actual_delivery and self.quality_rating:
            supplier = self.supplier
            # Update on-time delivery rate
            on_time = self.actual_delivery <= self.expected_delivery
            total_delivered = SupplierOrder.objects.filter(
                supplier=supplier, 
                actual_delivery__isnull=False
            ).count()
            on_time_count = SupplierOrder.objects.filter(
                supplier=supplier,
                actual_delivery__lte=F('expected_delivery')
            ).count()
            supplier.on_time_delivery_rate = on_time_count / total_delivered
            
            # Update quality rating
            avg_quality = SupplierOrder.objects.filter(
                supplier=supplier,
                quality_rating__isnull=False
            ).aggregate(Avg('quality_rating'))['quality_rating__avg']
            supplier.quality_rating = avg_quality
            
            supplier.total_orders = SupplierOrder.objects.filter(
                supplier=supplier
            ).count()
            supplier.last_order_date = self.order_date
            supplier.calculate_performance_score()

class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_date = models.DateTimeField(auto_now_add=True)
    expected_delivery = models.DateField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    received = models.BooleanField(default=False)
    
    @property
    def total_cost(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        if self.received:
            self.inventory_item.current_stock += self.quantity
            self.inventory_item.save()
        super().save(*args, **kwargs)

class LeaveType(models.Model):
    name = models.CharField(max_length=50)  # e.g., Sick Leave, Vacation, Personal
    paid = models.BooleanField(default=True)
    max_days_per_year = models.PositiveIntegerField()
    requires_approval = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled')
    ]
    
    staff = models.ForeignKey('StaffProfile', on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey('StaffProfile', on_delete=models.SET_NULL, null=True, related_name='approved_leaves')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date")
        
        # Check remaining leave balance
        used_days = self.staff.get_used_leave_days(self.leave_type)
        requested_days = (self.end_date - self.start_date).days + 1
        if used_days + requested_days > self.leave_type.max_days_per_year:
            raise ValidationError("Insufficient leave balance")

class ShiftSwapRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled')
    ]
    
    requester_shift = models.ForeignKey('Shift', on_delete=models.CASCADE, related_name='swap_requests_made')
    requested_shift = models.ForeignKey('Shift', on_delete=models.CASCADE, related_name='swap_requests_received')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey('StaffProfile', on_delete=models.SET_NULL, null=True, related_name='approved_swaps')

class OvertimeRecord(models.Model):
    staff = models.ForeignKey('StaffProfile', on_delete=models.CASCADE)
    date = models.DateField()
    hours = models.DecimalField(max_digits=4, decimal_places=2)
    reason = models.TextField()
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey('StaffProfile', on_delete=models.SET_NULL, null=True, related_name='approved_overtime')
    rate_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.5)
    
    @property
    def overtime_pay(self):
        base_hourly = self.staff.salary / (52 * 40)  # Assuming 40-hour work week
        return base_hourly * self.hours * self.rate_multiplier

class PerformanceMetric(models.Model):
    METRIC_TYPES = [
        ('ATTENDANCE', 'Attendance Rate'),
        ('TASK_COMPLETION', 'Task Completion Rate'),
        ('CUSTOMER_RATING', 'Customer Rating'),
        ('EFFICIENCY', 'Efficiency Score')
    ]
    
    staff = models.ForeignKey('StaffProfile', on_delete=models.CASCADE)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    value = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()
    notes = models.TextField(blank=True)

class PerformanceReview(models.Model):
    staff = models.ForeignKey('StaffProfile', on_delete=models.CASCADE)
    reviewer = models.ForeignKey('StaffProfile', on_delete=models.CASCADE, related_name='reviews_given')
    review_date = models.DateField()
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comments = models.TextField()
    goals_set = models.TextField()
    next_review_date = models.DateField()

class RoomServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent')
    ]
    
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE)
    service_type = models.CharField(max_length=20, choices=SERVICES_TYPES)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    assigned_to = models.ForeignKey('StaffProfile', on_delete=models.SET_NULL, null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_duration = models.DurationField(null=True, blank=True)
    room_number = models.CharField(max_length=10)
    guest_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.service_type} - Room {self.room_number}"

class RoomServiceFeedback(models.Model):
    service_request = models.OneToOneField(RoomServiceRequest, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback for {self.service_request}"

class RoomServiceLog(models.Model):
    service_request = models.ForeignKey(RoomServiceRequest, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=RoomServiceRequest.STATUS_CHOICES)
    notes = models.TextField(blank=True)
    logged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        