from django.db import models
from django.utils import timezone
from hotel.models import Hotel, Room, RoomType, RoomServiceFeedback
from booking.models import Booking
from django.db.models import Sum, Avg, Count
from datetime import timedelta
from django.db.models import Subquery, OuterRef, FloatField
from decimal import Decimal

class AnalyticsReport(models.Model):
    REPORT_TYPES = [
        ('REVENUE', 'Revenue Analysis'),
        ('OCCUPANCY', 'Occupancy Analysis'),
        ('PERFORMANCE', 'Performance Metrics'),
        ('BOOKING', 'Booking Trends')
    ]
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()
    
    @classmethod
    def generate_revenue_report(cls, start_date, end_date):
        # Helper function to convert Decimal to float
        def decimal_to_float(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return obj

        # Get the raw data
        total_revenue = Booking.objects.filter(
            check_in_date__range=[start_date, end_date]
        ).aggregate(total=Sum('total'))['total'] or 0

        revenue_by_room_type = list(Booking.objects.filter(
            check_in_date__range=[start_date, end_date]
        ).values('room_type__type').annotate(
            total=Sum('total'),
            count=Count('id')
        ))

        daily_revenue = list(Booking.objects.filter(
            check_in_date__range=[start_date, end_date]
        ).values('check_in_date').annotate(
            total=Sum('total')
        ).order_by('check_in_date'))

        # Convert Decimal values to float
        data = {
            'total_revenue': decimal_to_float(total_revenue),
            'revenue_by_room_type': [
                {
                    'room_type__type': item['room_type__type'],
                    'total': decimal_to_float(item['total']),
                    'count': item['count']
                }
                for item in revenue_by_room_type
            ],
            'daily_revenue': [
                {
                    'check_in_date': item['check_in_date'].isoformat() if item['check_in_date'] else None,
                    'total': decimal_to_float(item['total'])
                }
                for item in daily_revenue
            ]
        }

        return cls.objects.create(
            report_type='REVENUE',
            start_date=start_date,
            end_date=end_date,
            data=data
        )
    
    @classmethod
    def generate_occupancy_report(cls, start_date, end_date):
        def decimal_to_float(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return obj

        # Get total rooms count
        total_rooms = Room.objects.count()
        
        # If no rooms exist, return default data
        if total_rooms == 0:
            return {
                'overall_occupancy': 0,
                'occupancy_by_type': [],
                'daily_occupancy': [{
                    'date': current_date.isoformat(),
                    'occupancy': 0
                } for current_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1))]
            }
        
        data = {
            'overall_occupancy': Room.objects.annotate(
                days_occupied=Count('booking',
                    filter=models.Q(
                        booking__check_in_date__range=[start_date, end_date]
                    )
                )
            ).aggregate(
                avg_occupancy=Avg('days_occupied')
            )['avg_occupancy'] or 0,
            
            'occupancy_by_type': list(RoomType.objects.annotate(
                occupancy_rate=models.ExpressionWrapper(
                    Count('room__booking',
                        filter=models.Q(
                            room__booking__check_in_date__range=[start_date, end_date]
                        )
                    ) * 100.0 / Count('room'),
                    output_field=models.FloatField()
                )
            ).values('type', 'occupancy_rate')),
            
            'daily_occupancy': []
        }
        
        current_date = start_date
        while current_date <= end_date:
            occupied_rooms = Room.objects.filter(
                booking__check_in_date__lte=current_date,
                booking__check_out_date__gte=current_date
            ).count()
            
            data['daily_occupancy'].append({
                'date': current_date.isoformat(),
                'occupancy': (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
            })
            current_date += timedelta(days=1)
        
        return cls.objects.create(
            report_type='OCCUPANCY',
            start_date=start_date,
            end_date=end_date,
            data=data
        )
    
    @classmethod
    def generate_performance_report(cls, start_date, end_date):
        def decimal_to_float(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, timedelta):
                return obj.days  # Convert timedelta to number of days
            return obj

        # Get service ratings through a subquery
        service_ratings = RoomServiceFeedback.objects.filter(
            service_request__booking__room_type=OuterRef('pk'),
            submitted_at__range=[start_date, end_date]
        ).values('service_request__booking__room_type').annotate(
            avg_rating=Avg('rating')
        ).values('avg_rating')

        # Calculate average stay length
        avg_stay = Booking.objects.filter(
            check_in_date__range=[start_date, end_date]
        ).annotate(
            stay_length=(models.F('check_out_date') - models.F('check_in_date'))
        ).aggregate(
            avg=Avg('stay_length')
        )['avg'] or timedelta(days=0)

        data = {
            'average_stay_length': decimal_to_float(avg_stay),  # Convert timedelta to days
            
            'cancellation_rate': (
                Booking.objects.filter(
                    check_in_date__range=[start_date, end_date],
                    status='cancelled'
                ).count() /
                max(Booking.objects.filter(
                    check_in_date__range=[start_date, end_date]
                ).count(), 1) * 100
            ),
            
            'room_type_popularity': list(RoomType.objects.annotate(
                booking_count=Count('booking',
                    filter=models.Q(
                        booking__check_in_date__range=[start_date, end_date]
                    )
                )
            ).values('type', 'booking_count')),
            
            'service_ratings': list(RoomType.objects.annotate(
                avg_rating=Subquery(service_ratings, output_field=FloatField())
            ).values('type', 'avg_rating'))
        }
        
        # Convert any Decimal or timedelta values to float/int
        data = {
            key: decimal_to_float(value) if isinstance(value, (Decimal, timedelta)) else value
            for key, value in data.items()
        }
        
        return cls.objects.create(
            report_type='PERFORMANCE',
            start_date=start_date,
            end_date=end_date,
            data=data
        )

class DashboardWidget(models.Model):
    WIDGET_TYPES = [
        ('REVENUE_CHART', 'Revenue Chart'),
        ('OCCUPANCY_CHART', 'Occupancy Chart'),
        ('PERFORMANCE_METRICS', 'Performance Metrics'),
        ('BOOKING_TRENDS', 'Booking Trends')
    ]
    
    name = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    position = models.PositiveIntegerField()
    is_visible = models.BooleanField(default=True)
    settings = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['position']
