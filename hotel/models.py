

from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.template.defaultfilters import escape
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe

from userauths.models import User

import shortuuid
from taggit.managers import TaggableManager


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
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
            
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
        return f"{self.type}"

    def rooms_count(self):
        return Room.objects.filter(room_type=self).count()
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
            
        super(RoomType, self).save(*args, **kwargs) 
    

class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)
    rid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hotel.name} - Room {self.room_number}"

    def price(self):
        return self.room_type.price
    
    def number_of_beds(self):
        return self.room_type.number_of_beds
    


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True)
    room = models.ManyToManyField(Room)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    num_adults = models.PositiveIntegerField(default=1)
    num_children = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    booking_id = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")


    def __str__(self):
        return f"{self.room.hotel.name} - Room {self.room.room_number}"


class RoomServices(models.Model):
    booking = models.ForeignKey(Booking, null=True, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    service_type = models.CharField(max_length=20, choices=SERVICES_TYPES)
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)

    def str(self):
        return str(self.booking) + " " + str(self.room) + " " + str(self.service_type)

