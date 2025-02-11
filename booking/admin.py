from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Booking, Waitlist, BookingPackage, CancellationPolicy
from hotel.models import InventoryAlert
from django.http import HttpResponse
import csv

# Register your models here.

class WaitlistInline(admin.TabularInline):
    model = Waitlist
    extra = 0

class BookingPackageInline(admin.TabularInline):
    model = BookingPackage.included_room_types.through
    extra = 1

@admin.register(Booking)
class BookingAdmin(ImportExportModelAdmin):
    list_display = ['user', 'hotel', 'room_type', 'check_in_date', 
                   'check_out_date', 'is_group_booking', 'package', 
                   'cancellation_policy']
    list_editable = ['cancellation_policy']
    list_filter = ['is_group_booking', 'package', 'cancellation_policy']
    actions = ['mass_cancel', 'export_csv', 'apply_discount']

    def mass_cancel(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"{updated} bookings cancelled")
    mass_cancel.short_description = "Cancel selected bookings"
    
    def apply_discount(self, request, queryset):
        discount = request.POST.get('discount', 10)  # Get from input
        for booking in queryset:
            booking.total *= (1 - discount/100)
            booking.save()
        self.message_user(request, f"Applied {discount}% discount to {queryset.count()} bookings")
    
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bookings.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'User', 'Check-in', 'Check-out', 'Total', 'Status'])
        
        for booking in queryset:
            writer.writerow([
                booking.id,
                booking.user.email,
                booking.check_in_date,
                booking.check_out_date,
                booking.total,
                booking.status
            ])
        return response

@admin.register(Waitlist)
class WaitlistAdmin(ImportExportModelAdmin):
    list_display = ['user', 'room_type', 'check_in', 'check_out', 'created_at']
    list_filter = ['room_type', 'check_in']

@admin.register(BookingPackage)
class BookingPackageAdmin(ImportExportModelAdmin):
    list_display = ['name', 'discount', 'active']
    filter_horizontal = ['included_room_types']

@admin.register(CancellationPolicy)
class CancellationPolicyAdmin(ImportExportModelAdmin):
    list_display = ['name', 'hours_before_checkin', 'charge_percentage', 'active']
    list_editable = ['active']
