from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required


from hotel.models import Hotel, Room, Booking, RoomServices, HotelGallery, HotelFeatures, RoomType


def index(request):
    hotel = Hotel.objects.filter(status="Live")
    context = {
        "hotel":hotel
    }
    return render(request, "hotel/index.html", context)


def hotel_detail(request, slug):
    hotel = Hotel.objects.get(status="Live", slug=slug)
    context = {
        "hotel":hotel
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
    if 'selection_data_obj' in request.session:

        for h_id, item in request.session['selection_data_obj'].items():
            
            id = item['hotel_id']
            checkin = item["checkin"]
            checkout = item["checkout"]
            adult = item["adult"]
            children = item["children"]
            room_type_ = item["room_type"]

            
            print("item ===========", item)
            
        context = {
            "cart_data":request.session['selection_data_obj'], 
            'totalcartitems': len(request.session['selection_data_obj']), 
            
        }

        return render(request, "hotel/selected_rooms.html", context)
    else:
        messages.warning(request, "Your cart is empty, add something to the cart to continue")
        return redirect("/")

