from Leave.models import ShortAttendance, LeaveApplications
from employee.models import Attendance,Employee
from django.contrib.auth.models import User
from datetime import date,datetime, timedelta, time
from django.core.management.base import BaseCommand
import logging
import pytz
from string import Formatter

logger = logging.getLogger('MyANSRSource')


class Command(BaseCommand):
    help = 'Upload Leave summary for new joinee.'

    def handle(self, *args, **options):
        shortLeave()


#short leave check for every user in db


def shortLeave():
    # import ipdb
    # ipdb.set_trace()
    tzone = pytz.timezone('Asia/Kolkata')
    user_list = User.objects.filter(is_active = True)
    checkdate = date(2016,7,29)
    FMT = '%H:%M:%S'

    dueDate = checkdate + timedelta(days=30)
    morningInTimeLimit = datetime.strptime("10:15:00", FMT)
    fullDayOfficeStayTimeLimit = timedelta(hours =9, minutes = 00, seconds = 00)
    halfDayOfficeStayTimeLimit = timedelta(hours =4, minutes = 30, seconds = 00)

    for user in user_list:
        try:
            reason = ""
            shortLeaveType = ""
            employee = Employee.objects.filter(user_id = user.id)
            appliedLeaveCheck = LeaveApplications.objects.filter(from_date__lte=checkdate, to_date__gte=checkdate, user=user.id)
            manager_id = Employee.objects.filter(user_id=user).values('manager_id')
            manager = Employee.objects.filter(employee_assigned_id=manager_id).values('user_id')
            if manager:
                manager_d = User.objects.get(id=manager[0]['user_id'])
            else:
                manager_d = User.objects.get(id= 35)
            if employee:
                attendance = Attendance.objects.filter(attdate= checkdate, employee_id = employee[0].employee_assigned_id)
                if attendance:
                    swipeIn = attendance[0].swipe_in.astimezone(tzone)
                    swipeOut = attendance[0].swipe_out.astimezone(tzone)
                    swipeInTime = swipeIn.strftime("%H:%M:%S")
                    swipeOutTime = swipeOut.strftime("%H:%M:%S")
                    tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                    stayInTime = getTimeFromTdelta(tdelta, "{H:02}:{M:02}:{S:02}")
                    morningInTime = datetime.strptime(swipeInTime, FMT)
                    if tdelta < halfDayOfficeStayTimeLimit:
                        reason = "you had put {0} hours which is below 4.5 hours".format(stayInTime)
                        shortLeaveType = 'full_day'
                    elif tdelta < fullDayOfficeStayTimeLimit:
                        reason = "you had put {0} hours which is below 9 hours".format(stayInTime)
                        shortLeaveType = 'half_day'
                    elif morningInTime > morningInTimeLimit:
                        reason = "you came at {0}, you came late".format(morningInTime.time().isoformat())
                        shortLeaveType = 'half_day'
                else:
                    tdelta = timedelta(hours=0, minutes=0, seconds=0)
                    stayInTime = getTimeFromTdelta(tdelta, "{H:02}:{M:02}:{S:02}")
                    reason = "you were absent"
                    shortLeaveType = 'full_day'
                if  len(appliedLeaveCheck)>1:
                    pass
                elif len(appliedLeaveCheck)==1 and shortLeaveType == 'half_day':
                    pass
                elif len(appliedLeaveCheck)==1 and appliedLeaveCheck[0].from_date==checkdate and appliedLeaveCheck[0].to_date==checkdate and appliedLeaveCheck[0].from_session=='session_first' and appliedLeaveCheck[0].to_session== 'session_second':
                    pass
                elif len(appliedLeaveCheck)==1 and appliedLeaveCheck[0].from_date<checkdate and appliedLeaveCheck[0].to_date>checkdate:
                    pass
                elif len(appliedLeaveCheck)==1 and appliedLeaveCheck[0].from_date==checkdate and appliedLeaveCheck[0].to_date>checkdate and appliedLeaveCheck[0].from_session=='session_first':
                    pass
                elif len(appliedLeaveCheck) == 1 and appliedLeaveCheck[0].from_date < checkdate and appliedLeaveCheck[
                    0].to_date == checkdate and appliedLeaveCheck[0].to_session== 'session_second':
                    pass
                else:
                    if shortLeaveType:
                        ShortAttendance(user = user,
                        short_leave_type = shortLeaveType,
                        for_date=checkdate,
                        status="open",
                        status_action_by = User.objects.get(id=35),
                        status_comments = reason,
                        due_date = dueDate,
                        dispute = "open",
                        reason = reason,
                        stay_time = stayInTime,
                        apply_to = manager_d,
                        swipe_in = swipeInTime,
                        swipe_out = swipeOutTime
                        ).save()
            else:
                print(user.first_name + user.last_name + " hr need to take care")
        except:
            ShortAttendance(user=user,
                            short_leave_type='full_day',
                            for_date=checkdate,
                            status="open",
                            status_action_by=User.objects.get(id=35),
                            status_comments="missing record",
                            due_date=dueDate,
                            dispute="open",
                            reason="missing records",
                            apply_to=manager_d,
                            ).save()






def getTimeFromTdelta(tdelta, fmt):
    f = Formatter()
    d = {}
    l = {'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
    k = map( lambda x: x[1], list(f.parse(fmt)))
    rem = int(tdelta.total_seconds())

    for i in ('D', 'H', 'M', 'S'):
        if i in k and i in l.keys():
            d[i], rem = divmod(rem, l[i])

    return f.format(fmt, **d)
