from django.contrib import admin
from hotel.models import Hotel, Room, Booking, RoomServices, HotelGallery, HotelFeatures, HotelFAQs, RoomType, ActivityLog, StaffOnDuty, Coupon, CouponUsers, Notification, Bookmark, Review, InventoryCategory, InventoryItem, InventoryAlert, InventoryTransaction, Department, StaffProfile, Shift, Attendance, StaffTask, Supplier, PurchaseOrder
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

class ActivityLog_Tab(admin.TabularInline):
    model = ActivityLog

class StaffOnDuty_Tab(admin.TabularInline):
    model = StaffOnDuty

class CouponUsers_Tab(admin.TabularInline):
    model = CouponUsers

class InventoryCategoryInline(admin.TabularInline):
    model = InventoryCategory
    extra = 1

class InventoryItemInline(admin.TabularInline):
    model = InventoryItem
    extra = 1
    show_change_link = True

class InventoryAlertInline(admin.TabularInline):
    model = InventoryAlert
    extra = 0
    show_change_link = True

class InventoryTransactionInline(admin.TabularInline):
    model = InventoryTransaction
    extra = 0
    show_change_link = True

class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 1

class StaffProfileInline(admin.TabularInline):
    model = StaffProfile
    extra = 1

class ShiftInline(admin.TabularInline):
    model = Shift
    extra = 0

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0

class StaffTaskInline(admin.TabularInline):
    model = StaffTask
    extra = 0

class HotelAdmin(ImportExportModelAdmin):
    inlines = [
        HotelGallery_Tab,
        HotelFeatures_Tab,
        RoomType_Tab,
        Room_Tab,
        HotelFAQs_Tab,
        InventoryCategoryInline,
        DepartmentInline,
    ]
    search_fields = ['user__username', 'name']
    list_filter = ['featured', 'status']
    list_editable = ['status']
    list_display = ['thumbnail', 'user', 'name', 'status', 'featured', 'views']
    list_per_page = 100
    prepopulated_fields = {"slug": ("name", )}


class RoomAdmin(ImportExportModelAdmin):
    list_display = ['hotel', 'room_number', 'room_type', 'price', 'number_of_beds', 'is_available']
    list_per_page = 100


class BookingAdmin(ImportExportModelAdmin):
    inlines = [ActivityLog_Tab, StaffOnDuty_Tab]
    list_filter = ['hotel', 'room_type', 'check_in_date', 'check_out_date', 'is_active', 'checked_in', 'checked_out']
    list_display = ['booking_id', 'user', 'hotel', 'room_type', 'rooms', 'total', 'total_days', 'num_adults', 'num_children', 'check_in_date', 'check_out_date', 'is_active', 'checked_in', 'checked_out']
    search_fields = ['booking_id', 'user__username', 'user__email']
    list_per_page = 100


class RoomServicesAdmin(ImportExportModelAdmin):
    list_display = ['booking', 'room', 'date', 'price', 'service_type']
    list_per_page = 100

class CouponAdmin(ImportExportModelAdmin):
    inlines = [CouponUsers_Tab]
    list_editable = ['valid_from', 'valid_to', 'active', 'type']
    list_display = ['code', 'discount', 'type', 'redemption', 'valid_from', 'valid_to', 'active', 'date']
        
class NotificationAdmin(ImportExportModelAdmin):
    list_editable = ['seen', 'type']
    list_display = ['user', 'booking', 'type', 'seen', 'date']

class BookmarkAdmin(ImportExportModelAdmin):
    list_display = ['user', 'hotel']

class ReviewAdmin(admin.ModelAdmin):
    list_editable = ['active']
    list_display = ['user', 'hotel', 'review', 'reply', 'rating', 'active']

@admin.register(InventoryCategory)
class InventoryCategoryAdmin(ImportExportModelAdmin):
    list_display = ['name', 'hotel', 'reorder_threshold']
    list_filter = ['hotel']
    inlines = [InventoryItemInline]

@admin.register(InventoryItem)
class InventoryItemAdmin(ImportExportModelAdmin):
    list_display = ['name', 'category', 'current_stock', 'minimum_stock', 'last_restocked']
    inlines = [InventoryAlertInline, InventoryTransactionInline]

@admin.register(InventoryAlert)
class InventoryAlertAdmin(admin.ModelAdmin):
    list_display = ['item', 'alert_type', 'created_at', 'resolved']
    actions = ['mark_resolved']
    
    def mark_resolved(self, request, queryset):
        updated = queryset.update(resolved=True)
        self.message_user(request, f"{updated} alerts marked as resolved")
    mark_resolved.short_description = "Mark alerts as resolved"

@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin):
    list_display = ['name', 'hotel', 'staff_count']
    inlines = [StaffProfileInline]

    def staff_count(self, obj):
        return obj.staffprofile_set.count()

@admin.register(StaffProfile)
class StaffProfileAdmin(ImportExportModelAdmin):
    list_display = ['user', 'hotel', 'position', 'department']
    inlines = [ShiftInline, AttendanceInline, StaffTaskInline]
    search_fields = ['user__username', 'position']

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['staff', 'start_time', 'end_time', 'get_department', 'hours']
    list_filter = ['staff__department', 'start_time']
    
    def get_department(self, obj):
        return obj.staff.department
    get_department.short_description = 'Department'
    
    def hours(self, obj):
        return (obj.end_time - obj.start_time).total_seconds() / 3600

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['staff', 'date', 'status', 'hours_worked']
    list_editable = ['status']
    readonly_fields = ['clock_in', 'clock_out']
    
    def hours_worked(self, obj):
        if obj.clock_out:
            return (obj.clock_out - obj.clock_in).total_seconds() / 3600
        return None

@admin.register(StaffTask)
class StaffTaskAdmin(ImportExportModelAdmin):
    list_display = ['title', 'staff', 'due_date', 'priority', 'completed', 'status']
    list_editable = ['priority', 'completed']

@admin.register(Supplier)
class SupplierAdmin(ImportExportModelAdmin):
    list_display = ['name', 'contact_name', 'email', 'phone', 'rating']
    search_fields = ['name', 'contact_name']
    list_filter = ['rating']

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(ImportExportModelAdmin):
    list_display = ['supplier', 'inventory_item', 'quantity', 'total_cost', 'expected_delivery', 'received']
    list_editable = ['received']
    list_filter = ['received', 'supplier']

admin.site.register(Hotel, HotelAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(RoomServices, RoomServicesAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(Review, ReviewAdmin)

