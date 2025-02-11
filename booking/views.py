from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from hotel.models import Hotel, Room, RoomType, InventoryItem
from .models import Booking, Waitlist, CancellationPolicy, BookingPackage, GroupBooking, GroupMember
from .forms import GroupBookingForm, GroupMemberFormSet
from .reports import GroupBookingReportService

from datetime import datetime, timedelta
from decimal import Decimal
import logging
import json
import csv

logger = logging.getLogger(__name__)

def check_room_availability(request):
    try:
        if request.method != "POST":
            return JsonResponse({'error': 'Invalid method'}, status=405)
            
        data = json.loads(request.body)
        room_type = get_object_or_404(RoomType, id=data['room_type_id'])
        
        # Check inventory
        inventory_item = InventoryItem.objects.get(room_type=room_type)
        if inventory_item.current_stock < 1:
            return JsonResponse({'available': False, 'waitlist': True})
            
        # Existing availability logic...
        return JsonResponse({'available': True})
        
    except KeyError as e:
        logger.warning(f"Missing parameter: {str(e)}")
        return JsonResponse({'error': f'Missing parameter: {e}'}, status=400)
    except RoomType.DoesNotExist:
        logger.error(f"Invalid room type ID: {data.get('room_type_id')}")
        return JsonResponse({'error': 'Invalid room type'}, status=404)
    except Exception as e:
        logger.error(f"Availability check error: {str(e)}")
        return JsonResponse({'error': 'Server error'}, status=500)

def cancel_booking(request, booking_id):
    try:
        with transaction.atomic():
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)
            
            if booking.status == 'cancelled':
                return JsonResponse({'error': 'Booking already cancelled'}, status=400)
                
            now = timezone.now()
            checkin_time = booking.check_in_date
            hours_before = (checkin_time - now).total_seconds() / 3600
            
            # Find applicable policy
            policy = CancellationPolicy.objects.filter(
                hours_before_checkin__lte=hours_before
            ).order_by('-hours_before_checkin').first()
            
            if not policy:
                return JsonResponse({'error': 'Cancellation not allowed'}, status=400)
                
            # Calculate fee
            fee_percentage = policy.charge_percentage
            cancellation_fee = (booking.total * fee_percentage) / 100
            
            # Update booking
            booking.status = 'cancelled'
            booking.cancellation_fee = cancellation_fee
            booking.cancellation_policy = policy
            booking.save()
            
            # Restock inventory
            for room in booking.rooms.all():
                InventoryItem.objects.filter(
                    room_type=room.room_type
                ).update(current_stock=F('current_stock') + 1)
            
            return JsonResponse({
                'status': 'success',
                'cancellation_fee': cancellation_fee,
                'refund_amount': booking.total - cancellation_fee
            })
            
    except Exception as e:
        logger.error(f"Booking cancellation failed: {str(e)}")
        return JsonResponse({'error': 'Cancellation failed'}, status=500)

def booking_data(request, slug):
    hotel = Hotel.objects.get(status="Live", slug=slug)
    context = {
        "hotel":hotel,
    }
    return render(request, "booking/booking_data.html", context)


def add_to_selection(request):
    room_selection = {}

    room_selection[str(request.GET['id'])] = {
        'hotel_id': request.GET['hotel_id'],
        'hotel_name': request.GET['hotel_name'],
        'room_name': request.GET['room_name'],
        'room_price': request.GET['room_price'],
        'number_of_beds': request.GET['number_of_beds'],
        'room_number': request.GET['room_number'],
        'room_type': request.GET['room_type'],
        'room_id': request.GET['room_id'],
        'checkin': request.GET['checkin'],
        'checkout': request.GET['checkout'],
        'adult': request.GET['adult'],
        'children': request.GET['children'],
    }

    if 'selection_data_obj' in request.session:
        if str(request.GET['id']) in request.session['selection_data_obj']:

            selection_data = request.session['selection_data_obj']
            selection_data[str(request.GET['id'])]['adult'] = int(room_selection[str(request.GET['id'])]['adult'])
            selection_data[str(request.GET['id'])]['children'] = int(room_selection[str(request.GET['id'])]['children'])
            request.session['selection_data_obj'] = selection_data
        else:
            selection_data = request.session['selection_data_obj']
            selection_data.update(room_selection)
            request.session['selection_data_obj'] = selection_data
    else:
        request.session['selection_data_obj'] = room_selection
    data = {
        "data":request.session['selection_data_obj'], 
        'total_selected_items': len(request.session['selection_data_obj'])
        }
    return JsonResponse(data)


def delete_session(request):
    request.session.pop('selection_data_obj', None)
    return redirect(request.META.get("HTTP_REFERER"))


def delete_selection(request):
    hotel_id = str(request.GET['id'])
    if 'selection_data_obj' in request.session:
        if hotel_id in request.session['selection_data_obj']:
            selection_data = request.session['selection_data_obj']
            del request.session['selection_data_obj'][hotel_id]
            request.session['selection_data_obj'] = selection_data


    total = 0
    total_days = 0
    room_count = 0
    adult = 0 
    children = 0 
    checkin = "" 
    checkout = "" 
    children = 0 
    hotel = None

    if 'selection_data_obj' in request.session:
        for h_id, item in request.session['selection_data_obj'].items():
                
            id = int(item['hotel_id'])

            checkin = item["checkin"]
            checkout = item["checkout"]
            adult += int(item["adult"])
            children += int(item["children"])
            room_type_ = item["room_type"]
            
            hotel = Hotel.objects.get(id=id)
            room_type = RoomType.objects.get(id=room_type_)

            date_format = "%Y-%m-%d"
            checkin_date = datetime.strptime(checkin, date_format)
            checout_date = datetime.strptime(checkout, date_format)
            time_difference = checout_date - checkin_date
            total_days = time_difference.days

            room_count += 1
            days = total_days
            price = room_type.price

            room_price = price * room_count
            total = room_price * days
        
    
    context = render_to_string("hotel/async/selected_rooms.html", { "data":request.session['selection_data_obj'],  "total_selected_items": len(request.session['selection_data_obj']), "total":total, "total_days":total_days, "adult":adult, "children":children,    "checkin":checkin,    "checkout":checkout,    "hotel":hotel})

    print("data ======", context)
    
    return JsonResponse({"data": context, 'total_selected_items': len(request.session['selection_data_obj'])})

def waitlist_management(request):
    waitlist_entries = Waitlist.objects.filter(user=request.user)
    context = {
        'waitlist': waitlist_entries
    }
    return render(request, 'booking/waitlist.html', context)

def package_list(request):
    packages = BookingPackage.objects.filter(active=True)
    context = {
        'packages': packages
    }
    return render(request, 'booking/packages.html', context)

def send_waitlist_available_notification(user, booking):
    # Implement email or notification logic here
    subject = "Waitlist Opportunity Available"
    message = f"A room {booking.room_type.name} has become available!"
    user.email_user(subject, message)

def calculate_package_price(base_price, package):
    discounted_price = base_price * (1 - package.discount / 100)
    return discounted_price

@login_required
def create_group_booking(request):
    if request.method == 'POST':
        form = GroupBookingForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create group booking
                    group_booking = form.save(commit=False)
                    group_booking.group_leader = request.user
                    
                    # Calculate base price and apply group discount
                    base_price = calculate_base_price(
                        group_booking.group_size,
                        form.cleaned_data['room_type']
                    )
                    discount = group_booking.calculate_discount()
                    final_price = base_price * (1 - discount/100)
                    
                    # Create main booking
                    booking = Booking.objects.create(
                        user=request.user,
                        total=final_price,
                        is_group_booking=True,
                        # ... other booking fields
                    )
                    
                    group_booking.booking = booking
                    group_booking.discount_applied = discount
                    group_booking.save()
                    
                    # Handle member formset
                    member_formset = GroupMemberFormSet(
                        request.POST, instance=group_booking
                    )
                    if member_formset.is_valid():
                        member_formset.save()
                    else:
                        raise ValueError("Invalid member data")
                    
                messages.success(request, "Group booking created successfully!")
                return redirect('booking:group_booking_detail', pk=group_booking.pk)
                
            except Exception as e:
                messages.error(request, f"Error creating booking: {str(e)}")
                
    else:
        form = GroupBookingForm()
        member_formset = GroupMemberFormSet()
    
    return render(request, 'booking/group_booking_form.html', {
        'form': form,
        'member_formset': member_formset
    })

@login_required
def group_booking_detail(request, pk):
    booking = get_object_or_404(GroupBooking, pk=pk)
    members = booking.groupmember_set.all()
    
    context = {
        'booking': booking,
        'members': members,
    }
    return render(request, 'booking/group_booking_detail.html', context)

def calculate_base_price(group_size, room_type):
    """Calculate base price considering group size and room type"""
    base_price = room_type.price
    
    # Apply dynamic pricing based on group size
    if group_size >= 20:
        base_price *= 0.8  # 20% base reduction for very large groups
    elif group_size >= 10:
        base_price *= 0.9  # 10% base reduction for large groups
    
    # Consider season and demand
    season_multiplier = get_season_multiplier()
    demand_multiplier = get_demand_multiplier()
    
    return base_price * season_multiplier * demand_multiplier

def get_season_multiplier():
    """Get price multiplier based on season"""
    current_month = timezone.now().month
    if current_month in [6, 7, 8]:  # Peak season
        return 1.2
    elif current_month in [12, 1]:  # Holiday season
        return 1.3
    return 1.0

def get_demand_multiplier():
    """Get price multiplier based on current demand"""
    current_occupancy = calculate_current_occupancy()
    if current_occupancy > 80:
        return 1.2
    elif current_occupancy > 60:
        return 1.1
    return 1.0

@login_required
def group_booking_edit(request, pk):
    booking = get_object_or_404(GroupBooking, pk=pk)
    if request.method == 'POST':
        form = GroupBookingForm(request.POST, instance=booking)
        member_formset = GroupMemberFormSet(request.POST, instance=booking)
        if form.is_valid() and member_formset.is_valid():
            form.save()
            member_formset.save()
            messages.success(request, "Group booking updated successfully!")
            return redirect('booking:group_booking_detail', pk=booking.pk)
    else:
        form = GroupBookingForm(instance=booking)
        member_formset = GroupMemberFormSet(instance=booking)
    
    return render(request, 'booking/group_booking_form.html', {
        'form': form,
        'member_formset': member_formset,
        'is_edit': True
    })

@login_required
def group_booking_cancel(request, pk):
    if request.method == 'POST':
        booking = get_object_or_404(GroupBooking, pk=pk)
        booking.booking.status = 'cancelled'
        booking.booking.save()
        messages.success(request, "Group booking cancelled successfully!")
    return redirect('booking:group_booking_detail', pk=pk)

@login_required
def group_member_checkin(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        member = get_object_or_404(GroupMember, id=member_id)
        member.is_checked_in = True
        member.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def calculate_group_price(request):
    group_size = int(request.GET.get('group_size', 0))
    group_type = request.GET.get('group_type')
    room_type_id = request.GET.get('room_type')
    
    try:
        room_type = RoomType.objects.get(id=room_type_id)
        base_price = calculate_base_price(group_size, room_type)
        discount = calculate_group_discount(group_size, group_type)
        final_price = base_price * (1 - discount/100)
        
        return JsonResponse({
            'base_price': float(base_price),
            'discount_amount': float(base_price * discount/100),
            'final_price': float(final_price)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def group_booking_report(request, booking_id):
    """Generate report for a single group booking"""
    group_booking = get_object_or_404(GroupBooking, id=booking_id)
    report_service = GroupBookingReportService(group_booking)
    report = report_service.generate_single_booking_report()
    
    return render(request, 'booking/reports/group_booking_report.html', {
        'report': report
    })

@method_decorator(login_required, name='dispatch')
class PeriodicReportView(TemplateView):
    template_name = 'booking/reports/periodic_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from request parameters
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Generate report
        report = GroupBookingReportService.generate_periodic_report(
            start_date=start_date,
            end_date=end_date
        )
        
        context['report'] = report
        return context

@login_required
def report_dashboard(request):
    """Dashboard showing report options and summary"""
    # Get quick stats
    today = timezone.now()
    service = GroupBookingReportService()
    
    # Get reports for different periods
    daily_report = service.generate_periodic_report(
        start_date=today.date(),
        end_date=today.date()
    )
    
    weekly_report = service.generate_periodic_report(
        start_date=today - timedelta(days=7),
        end_date=today
    )
    
    monthly_report = service.generate_periodic_report(
        start_date=today - timedelta(days=30),
        end_date=today
    )
    
    context = {
        'daily_stats': daily_report['summary'],
        'weekly_stats': weekly_report['summary'],
        'monthly_stats': monthly_report['summary'],
        'recent_bookings': GroupBooking.objects.order_by('-booking__date')[:5]
    }
    
    return render(request, 'booking/reports/dashboard.html', context)

@login_required
def export_report(request):
    """Export report data as CSV"""
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Generate report
    report = GroupBookingReportService.generate_periodic_report(
        start_date=start_date,
        end_date=end_date
    )
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="group_bookings_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Group Bookings Report', f'{start_date} to {end_date}'])
    writer.writerow([])
    
    # Write summary
    writer.writerow(['Summary'])
    writer.writerow(['Total Bookings', report['summary']['total_bookings']])
    writer.writerow(['Total Revenue', f"${report['summary']['total_revenue']:.2f}"])
    writer.writerow(['Average Group Size', f"{report['summary']['average_group_size']:.1f}"])
    writer.writerow([])
    
    # Write booking types
    writer.writerow(['Booking Types'])
    writer.writerow(['Type', 'Count', 'Revenue'])
    for type_data in report['booking_types']:
        writer.writerow([
            type_data['group_type'],
            type_data['count'],
            f"${type_data['revenue']:.2f}"
        ])
    
    return response

