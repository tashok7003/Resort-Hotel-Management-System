from django.urls import path 
from booking import views 

app_name = "booking"

urlpatterns = [
    path("check_room_availability/", views.check_room_availability, name="check_room_availability"),
    path("delete_session/", views.delete_session, name="delete_session"),
    path("booking_data/<slug:slug>/", views.booking_data, name="booking_data"),

    # Ajax
    path("add_to_selection/", views.add_to_selection, name="add_to_selection"),
    path("delete_selection/", views.delete_selection, name="delete_selection"),
    
    path('waitlist/', views.waitlist_management, name='waitlist_management'),
    path('packages/', views.package_list, name='package_list'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

    # Group Booking URLs
    path('group/create/', views.create_group_booking, name='group_booking_create'),
    path('group/<int:pk>/', views.group_booking_detail, name='group_booking_detail'),
    path('group/<int:pk>/edit/', views.group_booking_edit, name='group_booking_edit'),
    path('group/<int:pk>/cancel/', views.group_booking_cancel, name='group_booking_cancel'),
    path('group/member/checkin/', views.group_member_checkin, name='group_member_checkin'),
    path('group/calculate-price/', views.calculate_group_price, name='calculate_group_price'),

    # Reports URLs
    path('reports/', views.report_dashboard, name='report_dashboard'),
    path('reports/booking/<int:booking_id>/', views.group_booking_report, name='group_booking_report'),
    path('reports/periodic/', views.PeriodicReportView.as_view(), name='periodic_report'),
    path('reports/export/', views.export_report, name='export_report'),
]