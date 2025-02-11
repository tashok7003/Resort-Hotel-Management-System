from django.shortcuts import render, redirect
from django.db import models
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg, ExpressionWrapper, Case, When, FloatField, F
from django.db.models.functions import TruncMonth
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db.models import Q

from hotel.models import Booking, Notification, Bookmark, Hotel, Room, Supplier, InventoryItem, PurchaseOrder, Shift
from userauths.models import Profile, User
from userauths.forms import ProfileUpdateForm, UserUpdateForm

@login_required
def dashboard(request):
    bookings = Booking.objects.filter(user=request.user, payment_status="paid")
    print("Total bookings:", bookings.count())
    
    total_spent = Booking.objects.filter(user=request.user, payment_status="paid").aggregate(amount=models.Sum('total'))
    print("Total spent:", total_spent)
    
    monthly_bookings = Booking.objects.filter(user=request.user).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        count=Count('id'),
        total=Sum('total')
    ).order_by('month')
    
    package_stats = Booking.objects.values('room_type__type').annotate(
        total_revenue=Sum('total'),
        avg_occupancy=Avg('room_type__room_capacity'),
        cancellation_rate=ExpressionWrapper(
            Count(Case(When(payment_status='cancelled', then=1))) * 100.0 / Count('id'),
            output_field=FloatField()
        )
    )
    print("Package stats:", list(package_stats))
    
    payment_methods = Booking.objects.values('payment_status').annotate(
        total=Sum('total'),
        count=Count('id')
    )
    
    context = {
        "bookings": bookings,
        "total_spent": total_spent,
        "monthly_bookings": list(monthly_bookings),
        "package_stats": package_stats,
        "payment_methods": list(payment_methods),
        "age_distribution": Profile.objects.aggregate(
            teens=Count(Case(When(birth_date__gte=timezone.now().date() - relativedelta(years=19), birth_date__lte=timezone.now().date() - relativedelta(years=13), then=1))),
            adults=Count(Case(When(birth_date__gte=timezone.now().date() - relativedelta(years=40), birth_date__lte=timezone.now().date() - relativedelta(years=20), then=1))),
            seniors=Count(Case(When(birth_date__lt=timezone.now().date() - relativedelta(years=40), then=1)))
        )
    }
    return render(request, "user_dashboard/dashboard.html", context)

@login_required
def booking_detail(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)

    context = {
        "booking":booking,
    }
    return render(request, "user_dashboard/booking_detail.html", context)

@login_required
def bookings(request):
    bookings = Booking.objects.filter(user=request.user, payment_status="paid")

    context = {
        "bookings":bookings,
    }
    return render(request, "user_dashboard/bookings.html", context)


@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user, seen=False)

    context = {
        "notifications":notifications,
    }
    return render(request, "user_dashboard/notifications.html", context)

def notification_filter(request):
    query = request.GET['query']
    if query == "all":
        notifications = Notification.objects.filter(user=request.user)
    elif query == "read":
        notifications = Notification.objects.filter(user=request.user, seen=True)
    elif query == "unread":
        notifications = Notification.objects.filter(user=request.user, seen=False)
    else:
        notifications = Notification.objects.filter(user=request.user)
    
    print("notifications ===", notifications)

    context = render_to_string("user_dashboard/async/notifications.html", {"notifications":notifications})
    print("data ======", context)

    return JsonResponse({"data":context})


def notification_mark_as_seen(request):
    id = request.GET['id']
    notification = Notification.objects.get(id=id)
    notification.seen = True
    notification.save()
    
    return JsonResponse({"data":"Marked As Seen"})


@login_required
def wallet(request):
    bookings = Booking.objects.filter(user=request.user, payment_status="paid")
    total_spent = Booking.objects.filter(user=request.user, payment_status="paid").aggregate(amount=models.Sum('total'))

    context = {
        "bookings":bookings,
        "total_spent":total_spent,
    }
    return render(request, "user_dashboard/wallet.html", context)



@login_required
def bookmark(request):
    bookmark = Bookmark.objects.filter(user=request.user)

    context = {
        "bookmark":bookmark,
    }
    return render(request, "user_dashboard/bookmark.html", context)



@login_required
def delete_bookmark(request, bid):
    bookmark = Bookmark.objects.filter(bid=bid)
    bookmark.delete()
    return redirect("dashboard:bookmark")


def add_to_bookmark(request):
    id = request.GET['id']
    hotel = Hotel.objects.get(id=id)
    if request.user.is_authenticated:
        bookmark = Bookmark.objects.filter(user=request.user, hotel=hotel)
        if bookmark.exists():
            bookmark = Bookmark.objects.get(user=request.user, hotel=hotel)
            bookmark.delete()
            return JsonResponse({"data":"Bookmark Deleted", "icon":"success"})
        else:
            Bookmark.objects.create(user=request.user, hotel=hotel)
            return JsonResponse({"data":"Hotel Bookmarked" , "icon":"success"})
    else:
        return JsonResponse({"data":"Login To Bookmark Hotel" , "icon":"warning"})


@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect("dashboard:profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        "profile":profile,
        "u_form":u_form,
        "p_form":p_form,
    }
    return render(request, "user_dashboard/profile.html", context)


@login_required
def password_changed(request):
    return render(request, "user_dashboard/password_changed.html")


@login_required
def add_review(request):
    id = request.GET['id']
    rating = request.GET['rating']
    review = request.GET['review']
    hotel = Hotel.objects.get(id=id)

    review_check = Review.objects.filter(user=request.user, hotel=hotel)
    if review_check.exists():
        return JsonResponse({"data":"Review Already Exists", "icon":"warning"})
    else:
        Review.objects.create(
            user=request.user,
            rating=rating,
            hotel=hotel,
            review=review
        )
        return JsonResponse({"data":"Review Submitted, Thank You." , "icon":"success"})

def analytics(request):
    # Occupancy rates
    total_rooms = Room.objects.count()
    occupied = Booking.objects.filter(
        check_in_date__lte=timezone.now(),
        check_out_date__gte=timezone.now()
    ).count()
    occupancy_rate = (occupied / total_rooms) * 100 if total_rooms else 0
    
    # Financial reports
    revenue = Booking.objects.filter(payment_status='paid').aggregate(
        total=Sum('total'),
        monthly=Sum('total', filter=Q(date__month=timezone.now().month)),
        annual=Sum('total', filter=Q(date__year=timezone.now().year))
    )
    
    context = {
        'occupancy_rate': occupancy_rate,
        'revenue': revenue,
        # Add more metrics
    }
    return render(request, 'dashboard/analytics.html', context)

@login_required
def supplier_management(request):
    suppliers = Supplier.objects.all()
    context = {'suppliers': suppliers}
    return render(request, 'dashboard/suppliers.html', context)

@login_required
def inventory_restock(request):
    low_stock = InventoryItem.objects.filter(current_stock__lt=F('minimum_stock'))
    recent_orders = PurchaseOrder.objects.order_by('-order_date')[:10]
    context = {
        'low_stock': low_stock,
        'recent_orders': recent_orders
    }
    return render(request, 'dashboard/inventory_restock.html', context)

@login_required
def staff_schedule(request):
    shifts = Shift.objects.filter(start_time__gte=timezone.now())
    context = {'shifts': shifts}
    return render(request, 'dashboard/staff_schedule.html', context)

@login_required
def group_bookings(request):
    if request.method == 'POST':
        group_size = request.POST.get('group_size')
        discount = request.POST.get('discount')
        # Save to database or session
        messages.success(request, 'Group booking configuration updated')
        return redirect('dashboard:group_bookings')
    return render(request, 'dashboard/group_bookings.html')