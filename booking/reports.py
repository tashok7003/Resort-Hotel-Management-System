from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from .models import GroupBooking, GroupPayment, GroupRoomAllocation

class GroupBookingReportService:
    def __init__(self, group_booking=None):
        self.group_booking = group_booking

    def generate_single_booking_report(self):
        """Generate report for a single group booking"""
        if not self.group_booking:
            raise ValueError("No group booking specified")

        allocations = GroupRoomAllocation.objects.filter(group_booking=self.group_booking)
        payments = GroupPayment.objects.filter(group_booking=self.group_booking)
        
        report = {
            'booking_details': {
                'group_name': self.group_booking.group_name,
                'group_type': self.group_booking.get_group_type_display(),
                'total_members': self.group_booking.groupmember_set.count(),
                'check_in': self.group_booking.booking.check_in_date,
                'check_out': self.group_booking.booking.check_out_date,
            },
            'financial_details': {
                'total_amount': self.group_booking.booking.total,
                'amount_paid': self.group_booking.total_paid,
                'remaining_amount': self.group_booking.get_remaining_payment(),
                'discount_applied': self.group_booking.discount_applied,
            },
            'room_allocation': {
                'total_rooms': allocations.count(),
                'room_types': allocations.values('room__room_type__type').annotate(
                    count=Count('id')
                ),
            },
            'payment_history': payments.values(
                'payment_date', 'amount', 'payment_method', 'paid_by__name'
            ),
        }
        return report

    @staticmethod
    def generate_periodic_report(start_date=None, end_date=None):
        """Generate report for all group bookings in a period"""
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()

        bookings = GroupBooking.objects.filter(
            booking__check_in_date__gte=start_date,
            booking__check_in_date__lte=end_date
        )

        report = {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
            },
            'summary': {
                'total_bookings': bookings.count(),
                'total_revenue': bookings.aggregate(
                    total=Sum('booking__total')
                )['total'] or 0,
                'average_group_size': bookings.aggregate(
                    avg=Avg('group_size')
                )['avg'] or 0,
            },
            'booking_types': bookings.values('group_type').annotate(
                count=Count('id'),
                revenue=Sum('booking__total')
            ),
            'occupancy_data': GroupRoomAllocation.objects.filter(
                group_booking__in=bookings
            ).values('room__room_type__type').annotate(
                total_nights=Count('id')
            ),
        }
        return report 