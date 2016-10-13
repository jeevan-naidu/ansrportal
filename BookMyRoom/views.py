from django.shortcuts import render
from models import RoomDetail, MeetingRoomBooking
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.generic import View
import datetime
from django.utils import timezone
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
import json
import ast
import pytz


# Create your views here.
TimingsList = [ ['08:00-08:30', '08:30-09:00', '09:00-09:30', '09:30-10:00'],
                ['10:00-10:30', '10:30-11:00', '11:00-11:30', '11:30-12:00'],
                ['12:00-12:30', '12:30-13:00', '13:00-13:30', '13:30-14:00'],
                ['14:00-14:30', '14:30-15:00', '15:00-15:30', '15:30-16:00'],
                ['16:00-16:30', '16:30-17:00', '17:00-17:30', '17:30-18:00'],
                ['18:00-18:30', '18:30-19:00', '19:00-19:30', '19:30-20:00'] ]


class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        return self.set_current - self.intersect

    def removed(self):
        return self.set_past - self.intersect

    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])

"""
{"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0}
{"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0,"oneThe Enterprises: karle_ground_floor08:00-08:30":0}

addedset([])

removedset(['oneThe Enterprises: karle_ground_floor08:00-08:30']) // new record

unchangedset(['3', '5', '4', '7', '6', '9', '8']) // ignore them

changedset([])

{"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0,"10":0}
{"3":0,"4":0,"5":0,"6":1,"7":0,"8":0,"9":0,"10":0}
addedset([])
removedset([])
unchangedset(['10', '3', '5', '4', '7', '9', '8']) // discard
changedset(['6']) // overridden by admin - update case

{"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0,"10":0}
{"4":0,"5":0,"6":0,"7":0,"8":0,"9":0,"10":0}
addedset(['3']) // to be removed
removedset([])
unchangedset(['10', '5', '4', '7', '6', '9', '8'])
changedset([])

"""


class BookMeetingRoomView(View):

    def get(self, request):
        if 'for_location' not in request.session:
            request.session['for_location'] = ''
        if 'for_date' not in request.session:
            request.session['for_date'] = ''
        return render(request, 'BookMyRoom/index.html', locals())

    def post(self, request):
        is_empty = False
        context_data = {'add': True, 'record_added': False, 'success_msg': None,
                        'html_data': None, 'errors': '', 'for_date': '' }

        if request.POST.get('on_load'):
            on_load = ast.literal_eval(request.POST.get('on_load'))
            on_submit = ast.literal_eval(request.POST.get('on_submit'))
            s = DictDiffer(on_load, on_submit)
            if len(s.added()) > 0:
                MeetingRoomBooking.objects.filter(pk__in=s.added()).delete()  # release room
                context_data['record_added'] = True
                context_data['success_msg'] = "Your changes are made successfully"
            if len(s.added()) == 0 and len(s.removed()) == 0 and len(s.changed()) == 0:
                is_empty = True

        if not request.POST.get('for_date'):
            context_data['errors'] += "\nPlease select date"
        else:
            for_date = request.POST.get('for_date')
        bookings_list = request.POST.getlist('BookingTime')

        if not bookings_list and is_empty == True:
            context_data['errors'] += "\nNo room selected."
        if not context_data['errors']:
            # print request.POST.getlist('BookingTime')
            for element in request.POST.getlist('BookingTime'):
                if "/" in element:
                    data_list = element.split("/")
                    room_id = int(data_list[0])
                    room_obj = RoomDetail.objects.get(id=room_id)
                    time_period_list = data_list[1].split("-")
                    from_time = time_period_list[0]
                    to_time = time_period_list[1]

                    from_time_obj = datetime.datetime.strptime(str(for_date)+"/"+str(from_time), '%Y-%m-%d/%H:%M')
                    to_time_obj = datetime.datetime.strptime(str(for_date)+"/"+str(to_time), '%Y-%m-%d/%H:%M')
                    try:
                        booking_obj = MeetingRoomBooking.objects.get(room=room_obj,
                                                                     from_time=from_time_obj,
                                                                     to_time=to_time_obj, status='booked')

                        context_data['errors'] = "Oops! :( Looks like someone else clicked\
                        <b>Submit</b> just before you did. Better luck next time."
                    except:
                        booking_obj = MeetingRoomBooking(booked_by=request.user, room=room_obj, status='booked',
                                                         from_time=from_time_obj, to_time=to_time_obj)
                        booking_obj.save()

                else:
                    # override condition by admin
                    MeetingRoomBooking.objects.filter(pk=int(element)).update(booked_by=request.user)
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
        # print bookings_list.query
        # print bookings_list.count()
        context_data['bookings_list'] = bookings_list
        context_data['success_msg'] = "Booked"
        template = render(request, 'BookMyRoom/BookRoomAndViewDetails.html', context_data)
        context_data['html_data'] = template.content
    context_data.pop('rooms_list')
    context_data.pop('bookings_list')
    return JsonResponse(context_data)


@csrf_exempt
def CancelBooking(request):
    partial_update = False
    fail = 0

    # import pdb
    # pdb.set_trace()
    json_data = json.loads(request.body)  # request.raw_post_data w/ Django < 1.4
    try:
        remarks = json_data['remarks']
        cancel_id = json_data['cancel_id']
    except KeyError:
        print "error"
    tmp_cancel = cancel_id.values()
    tmp_remark = remarks.keys()
    context_data = {'record_updated': False, 'user_mismatch': False}
    if tmp_remark:
            for i in tmp_cancel[:]:
                if i in tmp_remark:
                    tmp_remark.remove(i)
            actual_remark_ids = tmp_remark

            for i, val in enumerate(actual_remark_ids):
                print "id" + val
                print "remark  " + remarks[val]
                try:
                    MeetingRoomBooking.objects.filter(id=val).update(remark=remarks[val])
                except Exception, e:
                    print "im failing " + str(e)
                    fail += 1

    if tmp_cancel:
        booking_obj = MeetingRoomBooking.objects.filter(id__in=tmp_cancel)
        print booking_obj.query
        print booking_obj
        for obj in booking_obj:
            if obj.booked_by == request.user:
                obj.status = 'cancelled'
                try:
                    obj.save()
                except:
                    partial_update = True
    print partial_update
    print fail
    if not partial_update and fail == 0:
        context_data['record_updated'] = True
    else:
        context_data['user_mismatch'] = True
    print JsonResponse(context_data)

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
    

