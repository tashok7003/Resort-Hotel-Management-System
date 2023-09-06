from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse


from hotel.models import Hotel, Room, Booking, RoomServices, HotelGallery, HotelFeatures, RoomType

def check_room_availability(request):
    if request.method == "POST":
        id = request.POST.get("hotel-id")
        checkin = request.POST.get("checkin")
        checkout = request.POST.get("checkout")
        adult = request.POST.get("adult")
        children = request.POST.get("children")
        room_type = request.POST.get("room-type")

        hotel = Hotel.objects.get(status="Live", id=id)
        room_type = RoomType.objects.get(hotel=hotel, slug=room_type)
        
        print("id ====", id)
        print("room_type ====", room_type)
        print("checkin ====", checkin)
        print("checkout ====", checkout)
        print("adult ====", adult)
        print("children ====", children)

        # return redirect("hotel:room_type_detail", hotel.slug, room_type.slug)
        url = reverse("hotel:room_type_detail", args=[hotel.slug, room_type.slug])
        url_with_params = f"{url}?hotel-id={id}&checkin={checkin}&checkout={checkout}&adult={adult}&children={children}&room_type={room_type}"
        return HttpResponseRedirect(url_with_params)

    else:
        return redirect("hotel:index")



def add_to_selection(request):
    room_selection = {}

    room_selection[str(request.GET['id'])] = {
        'hotel_id': request.GET['hotel_id'],
        'hotel_name': request.GET['hotel_name'],
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


# 
