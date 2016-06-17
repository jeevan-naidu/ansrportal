from django import template
from Grievances.models import SATISFACTION_CHOICES
register = template.Library()
from datetime import datetime
#from django.utils.timezone import localtime
#from django.utils.timezone import get_default_timezone
from BookMyRoom.models import RoomDetail, MeetingRoomBooking
import datetime
from django.utils import timezone
import pytz

@register.filter
def Concat(for_date, time_period):
    """ return cancatination of 'for_date' and 'time_period' seperated by semicolon. This is provided to 'IsBooked' template tag function"""
    
    return str(for_date) +";"+ str(time_period)

@register.filter
def IsBooked(for_date_time_period, room_obj):
    
    temp_list = for_date_time_period.split(";")
    for_date = temp_list[0]
    time_period= temp_list[1]
    for_date_obj = datetime.datetime.strptime(for_date + "," + time_period.split("-")[0],  "%Y-%m-%d,%H:%M")
    utc_datetime_obj = timezone.make_aware(for_date_obj, timezone.get_current_timezone())
    utc_datetime_obj = utc_datetime_obj.astimezone(pytz.utc)
    obj_list = MeetingRoomBooking.objects.filter(from_time=utc_datetime_obj, room=room_obj, active=True)
    
    return True if obj_list else False


@register.filter
def BookedBy(for_date_time_period, room_obj):
    
    temp_list = for_date_time_period.split(";")
    for_date = temp_list[0]
    time_period= temp_list[1]
    for_date_obj = datetime.datetime.strptime(for_date + "," + time_period.split("-")[0],  "%Y-%m-%d,%H:%M")
    utc_datetime_obj = timezone.make_aware(for_date_obj, timezone.get_current_timezone())
    utc_datetime_obj = utc_datetime_obj.astimezone(pytz.utc)
    obj_list = MeetingRoomBooking.objects.filter(from_time=utc_datetime_obj, room=room_obj, active=True)
    if obj_list:
        obj = obj_list[0]
        return str(obj.booked_by.username)
    else:
        return None





#@register.filter
#def IsNew(registered_date):
#    current_date = datetime.now().replace(tzinfo=get_default_timezone())
#    registered_date = localtime(registered_date)
#    diff = current_date - registered_date
#    if diff.days < 5:
#        return True
#    else:
#        return False
#

#register.filter('GetFileNamefromPath', GetFileNamefromPath)