from django.shortcuts import render
from models import RoomDetail, MeetingRoomBooking
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.generic import View
import datetime
from django.utils import timezone
from django.utils.encoding import smart_str
import pytz


# Create your views here.
TimingsList = [ ['08:00-08:30', '08:30-09:00', '09:00-09:30', '09:30-10:00'],
                ['10:00-10:30', '10:30-11:00', '11:00-11:30', '11:30-12:00'],
                ['12:00-12:30', '12:30-13:00', '13:00-13:30', '13:30-14:00'],
                ['14:00-14:30', '14:30-15:00', '15:00-15:30', '15:30-16:00'],
                ['16:00-16:30', '16:30-17:00', '17:00-17:30', '17:30-18:00'],
                ['18:00-18:30', '18:30-19:00', '19:00-19:30', '19:30-20:00'] ]


class BookMeetingRoomView(View):
    ''' add or edit grievances '''
    
    def get(self, request):
        if 'for_location' not in request.session:
            request.session['for_location'] = ''
        if 'for_date' not in request.session:
            request.session['for_date'] = ''
        return render(request, 'BookMyRoom/index.html', locals())
    
    def post(self, request):
        
        context_data = {'add' : True, 'record_added' : False, 'success_msg' : None,
                        'html_data' : None, 'errors' : '', 'for_date':'' }
        if not request.POST.get('for_date'):
            context_data['errors'] += "\nPlease select date"
        else:
            for_date = request.POST.get('for_date')
        bookings_list = request.POST.getlist('BookingTime')
        if not bookings_list:
            context_data['errors'] += "\nNo room selected."
        if not context_data['errors']:
            for element in request.POST.getlist('BookingTime'):
                data_list = element.split("/")
                room_id = int(data_list[0])
                room_obj = RoomDetail.objects.get(id=room_id)
                time_period_list = data_list[1].split("-")
                from_time = time_period_list[0]
                to_time = time_period_list[1]
                
                from_time_obj = datetime.datetime.strptime(str(for_date)+"/"+str(from_time), '%Y-%m-%d/%H:%M')
                to_time_obj = datetime.datetime.strptime(str(for_date)+"/"+str(to_time), '%Y-%m-%d/%H:%M')
                try:
                    booking_obj = MeetingRoomBooking.objects.get(room=room_obj, from_time=from_time_obj, to_time=to_time_obj, status='booked')
                    
                    context_data['errors'] = "Oops! :( Looks like someone else clicked\
                    <b>Submit</b> just before you did. Better luck next time."
                except:
                    booking_obj = MeetingRoomBooking(booked_by=request.user, room=room_obj, status='booked', 
                                                from_time=from_time_obj, to_time=to_time_obj)
                    booking_obj.save()
                    context_data['record_added'] = True
                    context_data['success_msg'] = "Booked"
        return JsonResponse(context_data)


def GetBookingsView(request):
    
    context_data = {'html_data': '', 'rooms_list': [], 'bookings_list': [],
                    'TimingsList': TimingsList, 'for_date': '', 'errors': '', 'bookings_list': '',
                    'location':''}
    context_data['for_date'] = request.GET.get('for_date', '')
    location = request.GET.get('location', '')
    if location:
        request.session['for_location'] = location
    if context_data['for_date']:
        request.session['for_date'] = request.GET.get('for_date', '')

    context_data['location'] = location
    context_data['rooms_list'] = RoomDetail.objects.filter(active=True, location=location)
    if not context_data['for_date']:
        context_data['errors'] = 'Please select date'
    else:
        current_date_time_obj = datetime.datetime.now()
        utcnow_datetime_obj = timezone.make_aware(current_date_time_obj, timezone.get_current_timezone())
        bookings_list = MeetingRoomBooking.objects.filter(booked_by=request.user,
                                                          from_time__gte=utcnow_datetime_obj,
                                                          status='booked').order_by('from_time')
        context_data['bookings_list'] = bookings_list
        context_data['success_msg'] = "Booked"
        template = render(request, 'BookMyRoom/BookRoomAndViewDetails.html', context_data)
        context_data['html_data'] = template.content
    context_data.pop('rooms_list')
    context_data.pop('bookings_list')
    return JsonResponse(context_data)

def CancelBooking(request):
    
    booking_id = request.POST.get('cancel_id', '')
    context_data = {'record_updated':False, 'user_mismatch':False}
   
    booking_obj = MeetingRoomBooking.objects.get(id=int(booking_id))
    if booking_obj.booked_by == request.user:
        booking_obj.status = 'cancelled'
        booking_obj.save()
        context_data['record_updated'] = True
    else:
        context_data['user_mismatch'] = True
    
    return JsonResponse(context_data)


def GetAllRoomsList(request):



    get_date = request.GET.get('date')
    get_room = request.GET.get('room')
    get_token = request.GET.get('token')
    rooms_list = RoomDetail.objects.all()
    room_dict = {'karle_ground_floor': [], 'karle_second_floor': [], 'btp': []}
    for i in rooms_list:
        if i.location in room_dict:
            room_dict[i.location].append([smart_str(i.id), smart_str(i.room_name)])
        else:
            room_dict[i.location] = [[smart_str(i.id), smart_str(i.room_name)]]

    template = render(request, 'BookMyRoom/AppRoomsList.html', room_dict)
    context_data = {'record_updated': False, 'user_mismatch': False}

    return JsonResponse({'html_data':template.content})


def GetBookingDetails(request):


    room_id = int(request.GET['room_id'])
    room_obj = RoomDetail.objects.get(id=room_id)
    context_data = {'bookings_list': [], 'room_obj':room_obj, 'bookings_details': [] }
    current_date_time_obj = datetime.datetime.now()

    utcnow_datetime_obj = timezone.make_aware(current_date_time_obj, timezone.get_current_timezone())
    bookings_list = MeetingRoomBooking.objects.filter(from_time__startswith=utcnow_datetime_obj.date, room__id=room_id,
                                                      status='booked').order_by('from_time')
    timings_list = ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30',
                    '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30',
                    '18:00', '18:30', '19:00', '19:30']
    bookings_details = []

    for elm in timings_list:
        exists = False
        for obj in bookings_list:
            local_time = timezone.localtime(obj.from_time)
            temp_var = ""
            temp_var += '0' + str(local_time.hour) if len(str(local_time.hour)) < 2 else str(local_time.hour)
            temp_var += ':' + str(local_time.minute) + '0' if len(str(local_time.minute)) < 2 else ':' + str(local_time.minute)

            if temp_var == elm:
                full_name = str(obj.booked_by.first_name) + " " + str(obj.booked_by.last_name)
                bookings_details.append((temp_var, full_name))
                exists = True
                break
        if not exists:
            bookings_details.append((elm, "Vacant"))

    context_data['bookings_details'] = bookings_details
    template = render(request, 'BookMyRoom/AppRoomBookingDetails.html', context_data)
    return JsonResponse({'html_data':template.content})


    

