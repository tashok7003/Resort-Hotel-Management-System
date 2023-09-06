from django.contrib import admin
from hotel.models import Hotel, Room, Booking, RoomServices, HotelGallery, HotelFeatures, HotelFAQs, RoomType
from import_export.admin import ImportExportModelAdmin

class HotelGallery_Tab(admin.TabularInline):
    model = HotelGallery

class HotelFeatures_Tab(admin.TabularInline):
    model = HotelFeatures

class HotelFAQs_Tab(admin.TabularInline):
    model = HotelFAQs

class Room_Tab(admin.TabularInline):
    model = Room

class RoomType_Tab(admin.TabularInline):
    model = RoomType

class HotelAdmin(ImportExportModelAdmin):
    inlines = [HotelGallery_Tab, HotelFeatures_Tab, RoomType_Tab ,Room_Tab, HotelFAQs_Tab]
    search_fields = ['user__username', 'name']
    list_filter = ['featured', 'status']
    list_editable = ['status']
    list_display = ['thumbnail' ,'user',  'name', 'status', 'featured' ,'views']
    list_per_page = 100
    prepopulated_fields = {"slug": ("name", )}


class RoomAdmin(ImportExportModelAdmin):
    list_display = ['hotel' ,'room_number',  'room_type', 'price', 'number_of_beds' ,'is_available']
    list_per_page = 100


class BookingAdmin(ImportExportModelAdmin):
    list_display = ['booking_id', 'user', 'check_in_date', 'check_out_date', 'is_active']
    list_per_page = 100


class RoomServicesAdmin(ImportExportModelAdmin):
    list_display = ['booking' ,'room', 'date', 'price', 'service_type']
    list_per_page = 100

admin.site.register(Hotel, HotelAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(RoomServices, RoomServicesAdmin)

