from django.urls import path 
from hotel import views 

app_name = "hotel"

urlpatterns = [
    path("", views.index, name="index"),
    path("detail/<slug:slug>/", views.hotel_detail, name="detail"),
    path("detail/<slug:slug>/room-type/<slug:rt_slug>/", views.room_type_detail, name="room_type_detail"),
    path("selected_rooms/", views.selected_rooms, name="selected_rooms"),
]