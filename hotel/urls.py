from django.urls import path 
from hotel import views 
from .views import InventoryDashboardView, InventoryDetailView, StaffDashboardView, StaffDetailView, ShiftCreateView, clock_in_out

app_name = "hotel"

urlpatterns = [
    path("", views.index, name="index"),
    path("detail/<slug:slug>/", views.hotel_detail, name="detail"),
    path("detail/<slug:slug>/room-type/<slug:rt_slug>/", views.room_type_detail, name="room_type_detail"),
    path("selected_rooms/", views.selected_rooms, name="selected_rooms"),
    path("checkout/<booking_id>/", views.checkout, name="checkout"),
    path("invoice/<booking_id>/", views.invoice, name="invoice"),
    path("update_room_status/", views.update_room_status, name="update_room_status"),
    
    # Payment API
    path('api/checkout-session/<booking_id>/', views.create_checkout_session, name='api_checkout_session'),
    path('success/<booking_id>/', views.payment_success, name='success'),
    path('failed/<booking_id>/', views.payment_failed, name='failed'),
    path('inventory/', InventoryDashboardView.as_view(), name='inventory_dashboard'),
    path('inventory/<int:pk>/', InventoryDetailView.as_view(), name='inventory_detail'),
    path('inventory/alert/<int:alert_id>/resolve/', views.resolve_inventory_alert, name='resolve_alert'),
    path('staff/', StaffDashboardView.as_view(), name='staff_dashboard'),
    path('staff/<int:pk>/', StaffDetailView.as_view(), name='staff_detail'),
    path('staff/shifts/new/', ShiftCreateView.as_view(), name='create_shift'),
    path('staff/attendance/', clock_in_out, name='clock_in_out'),
    
    # Supplier Management URLs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    
    # Inventory Management URLs
    path('inventory/', views.inventory_dashboard, name='inventory_dashboard'),
    path('inventory/<int:pk>/transaction/', views.inventory_transaction, name='inventory_transaction'),
    path('inventory/<int:pk>/', views.inventory_detail, name='inventory_detail'),
    path('inventory/create/', views.inventory_create, name='inventory_create'),
]