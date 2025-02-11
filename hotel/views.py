from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import F
from django.contrib.auth.mixins import LoginRequiredMixin

from hotel.models import Coupon, CouponUsers, Hotel, Room, Booking, RoomServices, HotelGallery, HotelFeatures, RoomType, Notification, Bookmark, Review, InventoryItem, InventoryTransaction, InventoryAlert, StaffProfile, Shift, Attendance, StaffTask, Supplier, SupplierOrder, LeaveRequest, LeaveType, ShiftSwapRequest, OvertimeRecord, PerformanceMetric, PerformanceReview, RoomServiceRequest, RoomServiceFeedback, RoomServiceLog

from datetime import datetime
from decimal import Decimal
import stripe
import json
from .forms import (SupplierForm, SupplierOrderForm, 
                   InventoryItemForm, InventoryTransactionForm,
                   LeaveRequestForm, ShiftSwapRequestForm, OvertimeRecordForm,
                   PerformanceMetricForm, PerformanceReviewForm,
                   RoomServiceRequestForm, RoomServiceAssignmentForm, 
                   RoomServiceFeedbackForm, RoomServiceStatusUpdateForm)


def index(request):
    hotel = Hotel.objects.filter(status="Live")
    context = {
        "hotel":hotel
    }
    return render(request, "hotel/index.html", context)


def hotel_detail(request, slug):
    hotel = Hotel.objects.get(status="Live", slug=slug)
    try:
        reviews = Review.objects.filter(user=request.user, hotel=hotel)
    except:
        reviews = None
    all_reviews = Review.objects.filter(hotel=hotel, active=True)
    
    if request.user.is_authenticated:
        bookmark = Bookmark.objects.filter(user=request.user, hotel=hotel)
    else:
        bookmark = None
    context = {
        "hotel":hotel,
        "bookmark":bookmark,
        "reviews":reviews,
        "all_reviews":all_reviews,
    }
    return render(request, "hotel/hotel_detail.html", context)


def room_type_detail(request, slug, rt_slug):
    hotel = Hotel.objects.get(status="Live", slug=slug)
    room_type = RoomType.objects.get(hotel=hotel, slug=rt_slug)
    rooms = Room.objects.filter(room_type=room_type, is_available=True)

    id = request.GET.get("hotel-id")
    checkin = request.GET.get("checkin")
    checkout = request.GET.get("checkout")
    adult = request.GET.get("adult")
    children = request.GET.get("children")
    room_type_ = request.GET.get("room-type")

    print("checkin ======", checkin)

    if not all([checkin, checkout]):
        messages.warning(request, "Please enter your booking data to check availability.")
        return redirect("booking:booking_data", hotel.slug)

    context = {
        "hotel":hotel,
        "room_type":room_type,
        "rooms":rooms,
        "id":id,
        "checkin":checkin,
        "checkout":checkout,
        "adult":adult,
        "children":children,
        "room_type_":room_type_,
    }
    return render(request, "hotel/room_type_detail.html", context)



def selected_rooms(request):
    # request.session.pop('selection_data_obj', None)

    total = 0
    room_count = 0
    total_days = 0
    adult = 0 
    children = 0 
    checkin = "0" 
    checkout = "" 
    children = 0 
    
    if 'selection_data_obj' in request.session:

        if request.method == "POST":
            for h_id, item in request.session['selection_data_obj'].items():
                
                id = int(item['hotel_id'])
                hotel_id = int(item['hotel_id'])

                checkin = item["checkin"]
                checkout = item["checkout"]
                adult = int(item["adult"])
                children = int(item["children"])
                room_type_ = item["room_type"]
                room_id = int(item["room_id"])
                
                user = request.user
                hotel = Hotel.objects.get(id=id)
                room = Room.objects.get(id=room_id)
                room_type = RoomType.objects.get(id=room_type_)

                

                
            date_format = "%Y-%m-%d"
            checkin_date = datetime.strptime(checkin, date_format)
            checout_date = datetime.strptime(checkout, date_format)
            time_difference = checout_date - checkin_date
            total_days = time_difference.days

            full_name = request.POST.get("full_name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")

            booking = Booking.objects.create(
                hotel=hotel,
                room_type=room_type,
                check_in_date=checkin,
                check_out_date=checkout,
                total_days=total_days,
                num_adults=adult,
                num_children=children,
                full_name=full_name,
                email=email,
                phone=phone
            )

            if request.user.is_authenticated:
                booking.user = request.user
                booking.save()
            else:
                booking.user = None
                booking.save()


            for h_id, item in request.session['selection_data_obj'].items():
                room_id = int(item["room_id"])
                room = Room.objects.get(id=room_id)
                booking.room.add(room)

                room_count += 1
                days = booking.total_days
                price = booking.room_type.price

                room_price = price * room_count
                total = room_price * days

                # print("room_price ==",room_price)
                # print("total ==",total)
            
            booking.total += float(total)
            booking.before_discount += float(total)
            booking.save()

            messages.success(request, "Checkout Now!")
            return redirect("hotel:checkout", booking.booking_id)

        hotel = None

        for h_id, item in request.session['selection_data_obj'].items():
                
            id = int(item['hotel_id'])
            hotel_id = int(item['hotel_id'])

            checkin = item["checkin"]
            checkout = item["checkout"]
            adult = int(item["adult"])
            children = int(item["children"])
            room_type_ = item["room_type"]
            room_id = int(item["room_id"])
            
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
            
            hotel = Hotel.objects.get(id=id)

        print("hotel ===", hotel)
        context = {
            "data":request.session['selection_data_obj'], 
            "total_selected_items": len(request.session['selection_data_obj']),
            "total":total,
            "total_days":total_days,
            "adult":adult,
            "children":children,   
            "checkin":checkin,   
            "checkout":checkout,   
            "hotel":hotel,   
        }

        return render(request, "hotel/selected_rooms.html", context)
    else:
        messages.warning(request, "You don't have any room selections yet!")
        return redirect("/")

def checkout(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)

    if booking.payment_status == "paid":
        messages.success(request, "This order has been paid for!")
        return redirect("/")
    else:
        booking.payment_status = "processing"
        booking.save()


    # Coupon
    now = timezone.now()
    if request.method == "POST":
        # Get code entered in the input field
        code = request.POST.get('code')
        print("code ======", code)
        try:
            coupon = Coupon.objects.get(code__iexact=code,valid_from__lte=now,valid_to__gte=now,active=True)
            if coupon in booking.coupons.all():
                messages.warning(request, "Coupon Already Activated")
                return redirect("hotel:checkout", booking.booking_id)
            else:
                CouponUsers.objects.create(
                    booking=booking,
                    coupon=coupon,
                    full_name=booking.full_name,
                    email=booking.email,
                    mobile=booking.phone,
                )

                if coupon.type == "Percentage":
                    discount = booking.total * coupon.discount / 100
                else:
                    discount = coupon.discount

                booking.coupons.add(coupon)
                booking.total -= discount
                booking.saved += discount
                booking.save()

                
                messages.success(request, "Coupon Found and Activated")
                return redirect("hotel:checkout", booking.booking_id)
        except Coupon.DoesNotExist:
            messages.error(request, "Coupon Not Found")
            return redirect("hotel:checkout", booking.booking_id)
    
    context = {
        "booking":booking,  
        "stripe_publishable_key":settings.STRIPE_PUBLIC_KEY,
        "flutter_publick_key":settings.FLUTTERWAVE_PUBLIC,
        "website_address":settings.WEBSITE_ADDRESS,
    }
    return render(request, "hotel/checkout.html", context)


@csrf_exempt
def create_checkout_session(request, booking_id):
    request_data = json.loads(request.body)
    booking = get_object_or_404(Booking, booking_id=booking_id)

    stripe.api_key = settings.STRIPE_PRIVATE_KEY
    checkout_session = stripe.checkout.Session.create(
        customer_email = booking.email,
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                    'name': booking.full_name,
                    },
                    'unit_amount': int(booking.total * 100),
                },
                'quantity': 1,
            }
        ],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('hotel:success', args=[booking.booking_id])) + "?session_id={CHECKOUT_SESSION_ID}&success_id="+booking.success_id+'&booking_total='+str(booking.total),
        cancel_url=request.build_absolute_uri(reverse('hotel:failed', args=[booking.booking_id]))+ "?session_id={CHECKOUT_SESSION_ID}",
    )

    booking.payment_status = "processing"
    booking.stripe_payment_intent = checkout_session['id']
    booking.save()

    print("checkout_session ==============", checkout_session)
    return JsonResponse({'sessionId': checkout_session.id})


def payment_success(request, booking_id):
    success_id = request.GET.get('success_id')
    booking_total = request.GET.get('booking_total')

    if success_id and booking_total: 
        success_id = success_id.rstrip('/')
        booking_total = booking_total.rstrip('/')
        
        booking = Booking.objects.get(booking_id=booking_id, success_id=success_id)
        
        # Payment Verification
        if booking.total == Decimal(booking_total):
            if booking.payment_status == "processing": #processing #paid
                booking.payment_status = "paid"
                booking.save()

                noti = Notification.objects.create(booking=booking,type="Booking Confirmed",)
                if request.user.is_authenticated:
                    noti.user = request.user
                    noti.save()
                else:
                    noti = None
                    noti.save()

                # Delete the Room Sessions
                if 'selection_data_obj' in request.session:
                    del request.session['selection_data_obj']
                
                # Send Email To Customer
                merge_data = {
                    'booking': booking, 
                    'booking_rooms': booking.room.all(), 
                    'full_name': booking.full_name, 
                    'subject': f"Booking Completed - Invoice & Summary - ID: #{booking.booking_id}", 
                }
                subject = f"Booking Completed - Invoice & Summary - ID: #{booking.booking_id}"
                text_body = render_to_string("email/booking_completed.txt", merge_data)
                html_body = render_to_string("email/booking_completed.html", merge_data)
                
                msg = EmailMultiAlternatives(
                    subject=subject, 
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[booking.email], 
                    body=text_body
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send()
                    
            elif booking.payment_status == "paid":
                messages.success(request, f'Your booking has been completed.')
                return redirect("/")
            else:
                messages.success(request, 'Opps... Internal Server Error; please try again later')
                return redirect("/")
                
        else:
            messages.error(request, "Error: Payment Manipulation Detected, This payment have been cancelled")
            booking.payment_status = "failed"
            booking.save()
            return redirect("/")
    else:
        messages.error(request, "Error: Payment Manipulation Detected, This payment have been cancelled")
        booking = Booking.objects.get(booking_id=booking_id, success_id=success_id)
        booking.payment_status = "failed"
        booking.save()
        return redirect("/")
    
    context = {
        "booking": booking, 
        'rooms':booking.room.all(), 
    }
    return render(request, "hotel/payment_success.html", context) 


def payment_failed(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)
    booking.payment_status = "failed"
    booking.save()
                
    context = {
        "booking": booking, 
    }
    return render(request, "hotel/payment_failed.html", context) 


def invoice(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)

    context = {
        "booking":booking,  
        "room":booking.room.all(),  
    }
    return render(request, "hotel/invoice.html", context)

@csrf_exempt
def update_room_status(request):
    today = timezone.now().date()

    booking = Booking.objects.filter(is_active=True, payment_status="paid")   
    for b in booking:
        if b.checked_in_tracker != True:
            if b.check_in_date > today:
                b.checked_in_tracker = False
                b.save()

                for r in b.room.all():
                    r.is_available = True
                    r.save()
                

            else:
                b.checked_in_tracker = True
                b.save()

                for r in b.room.all():
                    r.is_available = False
                    r.save()
        else:
            if b.check_out_date > today:
                b.checked_out_tracker = False
                b.save()

                for r in b.room.all():
                    r.is_available = False
                    r.save()

            else:
                b.checked_out_tracker = True
                b.save()

                for r in b.room.all():
                    r.is_available = True
                    r.save()

            

    return HttpResponse(today)

class InventoryDashboardView(ListView):
    model = InventoryItem
    template_name = 'hotel/inventory_dashboard.html'
    context_object_name = 'inventory_items'

    def get_queryset(self):
        return InventoryItem.objects.filter(category__hotel=self.request.user.profile.hotel)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alerts'] = InventoryAlert.objects.filter(item__category__hotel=self.request.user.profile.hotel, resolved=False)
        return context

class InventoryDetailView(DetailView):
    model = InventoryItem
    template_name = 'hotel/inventory_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = InventoryTransaction.objects.filter(item=self.object).order_by('-timestamp')
        return context

def resolve_inventory_alert(request, alert_id):
    alert = get_object_or_404(InventoryAlert, id=alert_id)
    alert.resolved = True
    alert.save()
    return redirect('hotel:inventory_dashboard')

class StaffDashboardView(ListView):
    model = StaffProfile
    template_name = 'hotel/staff_dashboard.html'
    
    def get_queryset(self):
        return StaffProfile.objects.filter(hotel=self.request.user.profile.hotel)

class StaffDetailView(DetailView):
    model = StaffProfile
    template_name = 'hotel/staff_detail.html'

class ShiftCreateView(CreateView):
    model = Shift
    fields = ['staff', 'start_time', 'end_time', 'notes']
    template_name = 'hotel/shift_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

@login_required
def clock_in_out(request):
    if request.method == 'POST':
        staff_profile = request.user.staffprofile
        today = timezone.now().date()
        
        try:
            attendance = Attendance.objects.get(staff=staff_profile, date=today)
            if not attendance.clock_out:
                attendance.clock_out = timezone.now().time()
                attendance.save()
                messages.success(request, "Clocked out successfully")
        except Attendance.DoesNotExist:
            Attendance.objects.create(
                staff=staff_profile,
                date=today,
                clock_in=timezone.now().time(),
                status='PRESENT'
            )
            messages.success(request, "Clocked in successfully")
            
        return redirect('staff_dashboard')

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    context = {
        'suppliers': suppliers,
        'active_suppliers': suppliers.filter(active=True).count(),
        'total_orders': SupplierOrder.objects.count()
    }
    return render(request, 'hotel/supplier/list.html', context)

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    orders = SupplierOrder.objects.filter(supplier=supplier)
    context = {
        'supplier': supplier,
        'orders': orders,
        'performance_metrics': {
            'on_time_delivery': f"{supplier.on_time_delivery_rate * 100:.1f}%",
            'quality_rating': f"{supplier.quality_rating:.1f}/5",
            'total_orders': supplier.total_orders
        }
    }
    return render(request, 'hotel/supplier/detail.html', context)

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier created successfully.')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'hotel/supplier/form.html', {'form': form})

@login_required
def inventory_dashboard(request):
    items = InventoryItem.objects.all()
    alerts = InventoryAlert.objects.filter(resolved=False)
    context = {
        'items': items,
        'alerts': alerts,
        'low_stock_count': items.filter(current_stock__lte=F('minimum_stock')).count(),
        'total_value': sum(item.current_stock * item.unit_price for item in items)
    }
    return render(request, 'hotel/inventory/dashboard.html', context)

@login_required
def inventory_transaction(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        form = InventoryTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.item = item
            transaction.performed_by = request.user
            transaction.save()
            messages.success(request, 'Transaction recorded successfully.')
            return redirect('inventory_dashboard')
    else:
        form = InventoryTransactionForm()
    
    context = {
        'form': form,
        'item': item,
        'recent_transactions': InventoryTransaction.objects.filter(
            item=item
        ).order_by('-transaction_date')[:5]
    }
    return render(request, 'hotel/inventory/transaction.html', context)

@login_required
def inventory_detail(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    transactions = InventoryTransaction.objects.filter(item=item).order_by('-transaction_date')[:10]
    context = {
        'item': item,
        'transactions': transactions
    }
    return render(request, 'hotel/inventory/detail.html', context)

@login_required
def inventory_create(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inventory item created successfully.')
            return redirect('hotel:inventory_dashboard')
    else:
        form = InventoryItemForm()
    return render(request, 'hotel/inventory/form.html', {'form': form})

@login_required
def resolve_alert(request, alert_id):
    alert = get_object_or_404(InventoryAlert, id=alert_id)
    alert.resolved = True
    alert.save()
    messages.success(request, 'Alert marked as resolved.')
    return redirect('hotel:inventory_dashboard')

class LeaveRequestListView(LoginRequiredMixin, ListView):
    model = LeaveRequest
    template_name = 'hotel/staff/leave_requests.html'
    context_object_name = 'leave_requests'
    
    def get_queryset(self):
        if self.request.user.staffprofile.position == 'Manager':
            return LeaveRequest.objects.filter(staff__department=self.request.user.staffprofile.department)
        return LeaveRequest.objects.filter(staff=self.request.user.staffprofile)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'staffprofile'):
            context['leave_balance'] = {
                leave_type: leave_type.max_days_per_year - self.request.user.staffprofile.get_used_leave_days(leave_type)
                for leave_type in LeaveType.objects.all()
            }
        return context

class LeaveRequestCreateView(LoginRequiredMixin, CreateView):
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'hotel/staff/leave_request_form.html'
    success_url = reverse_lazy('hotel:leave_requests')
    
    def form_valid(self, form):
        form.instance.staff = self.request.user.staffprofile
        return super().form_valid(form)

class ShiftSwapListView(LoginRequiredMixin, ListView):
    model = ShiftSwapRequest
    template_name = 'hotel/staff/shift_swaps.html'
    context_object_name = 'swap_requests'
    
    def get_queryset(self):
        return ShiftSwapRequest.objects.filter(
            models.Q(requester_shift__staff=self.request.user.staffprofile) |
            models.Q(requested_shift__staff=self.request.user.staffprofile)
        )

class ShiftSwapCreateView(LoginRequiredMixin, CreateView):
    model = ShiftSwapRequest
    form_class = ShiftSwapRequestForm
    template_name = 'hotel/staff/shift_swap_form.html'
    success_url = reverse_lazy('hotel:shift_swaps')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.requester_shift = self.request.user.staffprofile.shift_set.get(
            id=self.kwargs['shift_id']
        )
        return super().form_valid(form)

class OvertimeRecordListView(LoginRequiredMixin, ListView):
    model = OvertimeRecord
    template_name = 'hotel/staff/overtime_records.html'
    context_object_name = 'overtime_records'
    
    def get_queryset(self):
        if self.request.user.staffprofile.position == 'Manager':
            return OvertimeRecord.objects.filter(staff__department=self.request.user.staffprofile.department)
        return OvertimeRecord.objects.filter(staff=self.request.user.staffprofile)

class OvertimeRecordCreateView(LoginRequiredMixin, CreateView):
    model = OvertimeRecord
    form_class = OvertimeRecordForm
    template_name = 'hotel/staff/overtime_form.html'
    success_url = reverse_lazy('hotel:overtime_records')
    
    def form_valid(self, form):
        form.instance.staff = self.request.user.staffprofile
        return super().form_valid(form)

class PerformanceMetricListView(LoginRequiredMixin, ListView):
    model = PerformanceMetric
    template_name = 'hotel/staff/performance_metrics.html'
    context_object_name = 'metrics'
    
    def get_queryset(self):
        return PerformanceMetric.objects.filter(staff=self.request.user.staffprofile)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['performance_score'] = self.request.user.staffprofile.get_performance_score()
        return context

class PerformanceReviewDetailView(LoginRequiredMixin, DetailView):
    model = PerformanceReview
    template_name = 'hotel/staff/performance_review.html'
    context_object_name = 'review'

@login_required
def approve_leave_request(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    if request.user.staffprofile.position == 'Manager':
        leave_request.status = 'APPROVED'
        leave_request.approved_by = request.user.staffprofile
        leave_request.save()
        messages.success(request, 'Leave request approved successfully.')
    return redirect('hotel:leave_requests')

@login_required
def approve_shift_swap(request, pk):
    swap_request = get_object_or_404(ShiftSwapRequest, pk=pk)
    if request.user.staffprofile.position == 'Manager':
        with transaction.atomic():
            # Swap the shifts
            requester_shift = swap_request.requester_shift
            requested_shift = swap_request.requested_shift
            
            temp_staff = requester_shift.staff
            requester_shift.staff = requested_shift.staff
            requested_shift.staff = temp_staff
            
            requester_shift.save()
            requested_shift.save()
            
            swap_request.status = 'APPROVED'
            swap_request.approved_by = request.user.staffprofile
            swap_request.save()
            
            messages.success(request, 'Shift swap approved successfully.')
    return redirect('hotel:shift_swaps')

@login_required
def approve_overtime(request, pk):
    overtime = get_object_or_404(OvertimeRecord, pk=pk)
    if request.user.staffprofile.position == 'Manager':
        overtime.approved = True
        overtime.approved_by = request.user.staffprofile
        overtime.save()
        messages.success(request, 'Overtime approved successfully.')
    return redirect('hotel:overtime_records')

@login_required
def room_service_dashboard(request):
    context = {
        'pending_requests': RoomServiceRequest.objects.filter(status='PENDING'),
        'in_progress': RoomServiceRequest.objects.filter(status='IN_PROGRESS'),
        'my_tasks': RoomServiceRequest.objects.filter(
            assigned_to=request.user.staffprofile,
            status__in=['ASSIGNED', 'IN_PROGRESS']
        )
    }
    return render(request, 'hotel/room_service/dashboard.html', context)

@login_required
def create_service_request(request):
    if request.method == 'POST':
        form = RoomServiceRequestForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.booking = request.user.current_booking  # You'll need to implement this
            service.room_number = request.user.current_booking.room.room_number
            service.guest_name = request.user.get_full_name()
            service.save()
            
            # Create initial log entry
            RoomServiceLog.objects.create(
                service_request=service,
                status='PENDING',
                notes='Service request created',
                logged_by=request.user
            )
            
            messages.success(request, 'Service request submitted successfully')
            return redirect('hotel:service_request_detail', pk=service.pk)
    else:
        form = RoomServiceRequestForm()
    
    return render(request, 'hotel/room_service/request_form.html', {'form': form})

@login_required
def service_request_detail(request, pk):
    service = get_object_or_404(RoomServiceRequest, pk=pk)
    logs = service.roomservicelog_set.all()
    
    if request.method == 'POST':
        status_form = RoomServiceStatusUpdateForm(request.POST)
        if status_form.is_valid():
            new_status = status_form.cleaned_data['status']
            notes = status_form.cleaned_data['notes']
            
            service.status = new_status
            if new_status == 'COMPLETED':
                service.completed_at = timezone.now()
            service.save()
            
            RoomServiceLog.objects.create(
                service_request=service,
                status=new_status,
                notes=notes,
                logged_by=request.user
            )
            
            messages.success(request, 'Status updated successfully')
            return redirect('hotel:service_request_detail', pk=pk)
    else:
        status_form = RoomServiceStatusUpdateForm(initial={'status': service.status})
    
    context = {
        'service': service,
        'logs': logs,
        'status_form': status_form
    }
    return render(request, 'hotel/room_service/request_detail.html', context)

@login_required
def assign_service_request(request, pk):
    service = get_object_or_404(RoomServiceRequest, pk=pk)
    
    if request.method == 'POST':
        form = RoomServiceAssignmentForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save(commit=False)
            service.status = 'ASSIGNED'
            service.save()
            
            RoomServiceLog.objects.create(
                service_request=service,
                status='ASSIGNED',
                notes=f'Assigned to {service.assigned_to.user.get_full_name()}',
                logged_by=request.user
            )
            
            messages.success(request, 'Service request assigned successfully')
            return redirect('hotel:service_request_detail', pk=pk)
    else:
        form = RoomServiceAssignmentForm(instance=service)
    
    return render(request, 'hotel/room_service/assign_form.html', {'form': form, 'service': service})

@login_required
def submit_service_feedback(request, pk):
    service = get_object_or_404(RoomServiceRequest, pk=pk)
    
    if request.method == 'POST':
        form = RoomServiceFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.service_request = service
            feedback.save()
            
            messages.success(request, 'Thank you for your feedback!')
            return redirect('hotel:service_request_detail', pk=pk)
    else:
        form = RoomServiceFeedbackForm()
    
    return render(request, 'hotel/room_service/feedback_form.html', {
        'form': form,
        'service': service
    })

@login_required
def get_service_status(request, pk):
    """AJAX endpoint for real-time status updates"""
    service = get_object_or_404(RoomServiceRequest, pk=pk)
    return JsonResponse({
        'status': service.status,
        'assigned_to': service.assigned_to.user.get_full_name() if service.assigned_to else None,
        'updated_at': service.roomservicelog_set.latest('timestamp').timestamp.isoformat(),
        'estimated_duration': str(service.estimated_duration) if service.estimated_duration else None
    })