from django.shortcuts import render
from models import RoomDetail, MeetingRoomBooking
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.generic import View
import datetime
from django.utils import timezone
import pytz


# Create your views here.
TimingsList = [ ['08:00-08:30', '08:30-09:00', '09:00-09:30', '09:30-10:00'],
                ['10:00-10:30', '10:30-11:00', '11:00-11:30', '11:30-12:00'],
                ['12:00-12:30', '12:30-13:00', '13:00-13:30', '13:30-14:00'],
                ['14:00-14:30', '14:30-15:00', '15:00-15:30', '15:30-16:30'],
                ['16:30-17:00', '17:00-17:30', '17:30-18:00', '18:00-18:30'],
                ['18:30-19:00', '19:00-19:30', '19:30-20:00', '20:00-20:30'] ]


class BookMeetingRoomView(View):
    ''' add or edit grievances '''
    
    def get(self, request):
        return render(request, 'BookMyRoom/index.html')
    
    def post(self, request):
        
        context_data = {'add' : True, 'record_added' : False, 'success_msg' : None,
                        'html_data' : None, 'errors' : [], 'for_date':'' }
        if not request.POST.get('for_date'):
            context_data['errors'].append("\nPlease select date")
        else:
            for_date = request.POST.get('for_date')
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
                booking_obj = MeetingRoomBooking(booked_by=request.user, room=room_obj,
                                                from_time=from_time_obj, to_time=to_time_obj)
                booking_obj.save()
                context_data['record_added'] = True
                context_data['success_msg'] = "Booked"
        return JsonResponse(context_data)
                
                                
      
    


    

def GetBookingsView(request):
    
    context_data = {'html_data': '', 'rooms_list': [], 'bookings_list': [],
                    'TimingsList': TimingsList, 'for_date': '', 'errors': '', 'bookings_list': ''}
    
    context_data['for_date'] = request.GET.get('for_date', '')
    location = request.GET.get('location', '')
    context_data['rooms_list'] = RoomDetail.objects.filter(active=True, location=location)
    if not context_data['for_date']:
        context_data['errors'] = 'Please select date'
    else:
        current_date_time_obj = datetime.datetime.now()
        utcnow_datetime_obj = timezone.make_aware(current_date_time_obj, timezone.get_current_timezone())
        bookings_list = MeetingRoomBooking.objects.filter(booked_by=request.user,
                                                          from_time__gte=utcnow_datetime_obj,
                                                          active=True).order_by('from_time')
        context_data['bookings_list'] = bookings_list
        context_data['success_msg'] = "Booked"
        template = render(request, 'BookMyRoom/BookRoomAndViewDetails.html', context_data)
        context_data['html_data'] = template.content
    context_data.pop('rooms_list')
    context_data.pop('bookings_list')
    return JsonResponse(context_data)

def CancelBooking(request):
    
    import ipdb;ipdb.set_trace()
    booking_id = request.POST.get('cancel_id', '')
    context_data = {'record_updated':False, 'user_mismatch':False}
   
    booking_obj = MeetingRoomBooking.objects.get(id=int(booking_id))
    if booking_obj.booked_by == request.user:
        booking_obj.active = False
        booking_obj.save()
        context_data['record_updated'] = True
    else:
        context_data['user_mismatch'] = True
    
    return JsonResponse(context_data)
    
    
# def BookMeetingRoomView(request):
#     import ipdb;ipdb.set_trace()
#     pass


    

