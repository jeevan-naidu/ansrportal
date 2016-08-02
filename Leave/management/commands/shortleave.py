from Leave.models import ShortLeave, LeaveApplications
from employee.models import Attendance,Employee
from django.contrib.auth.models import User
from datetime import date,datetime, timedelta, time
from django.core.management.base import BaseCommand
import logging
import pytz

logger = logging.getLogger('MyANSRSource')


class Command(BaseCommand):
    help = 'Upload Leave summary for new joinee.'

    def handle(self, *args, **options):
        shortLeave()


#short leave check for every user in db


def shortLeave():
    import ipdb
    ipdb.set_trace()
    tzone = pytz.timezone('Asia/Kolkata')
    user_list = User.objects.filter(is_active = True)
    checkdate = date(2016,7,12)
    FMT = '%H:%M:%S'

    dueDate = checkdate + timedelta(days=30)
    morningInTimeLimit = datetime.strptime("10:15:00", FMT)
    fullDayOfficeStayTimeLimit = timedelta(hours =8, minutes = 00, seconds = 00)
    halfDayOfficeStayTimeLimit = timedelta(hours =5, minutes = 00, seconds = 00)

    for user in user_list:
        reason = ""
        shortLeaveType = ""
        employee = Employee.objects.filter(user_id = user.id)
        appliedLeaveCheck = LeaveApplications.objects.filter(from_date__lte=checkdate, to_date__gte=checkdate, user=user.id)

        if employee:
            attendance = Attendance.objects.filter(attdate= checkdate, employee_id = employee[0].employee_assigned_id)
            if attendance:
                swipeIn = attendance[0].swipe_in.astimezone(tzone)
                swipeOut = attendance[0].swipe_out.astimezone(tzone)
                swipeInTime = swipeIn.strftime("%H:%M:%S")
                swipeOutTime = swipeOut.strftime("%H:%M:%S")
                tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                if tdelta < halfDayOfficeStayTimeLimit:
                    reason = "you are not avaliable for full day"
                    shortLeaveType = 'full_day'
                elif tdelta < fullDayOfficeStayTimeLimit:
                    reason = " you are not avaliable for half day"
                    shortLeaveType = 'half_day'
                elif datetime.strptime(swipeInTime, FMT) > morningInTimeLimit:
                    reason = "you were late"
                    shortLeaveType = 'half_day'
            else:
                reason = "you were absent"
                shortLeaveType = 'full_day'
            if  len(appliedLeaveCheck)>1:
                pass
            elif len(appliedLeaveCheck)==1 and shortLeaveType == 'half_day':
                pass
            elif len(appliedLeaveCheck)==1 and appliedLeaveCheck[0].from_date==checkdate and appliedLeaveCheck[0].to_date==checkdate and appliedLeaveCheck[0].from_session=='session_first' and appliedLeaveCheck[0].to_session== 'session_second':
                pass
            elif len(appliedLeaveCheck)==1 and appliedLeaveCheck[0].from_date<checkdate and appliedLeaveCheck[0].to_date<checkdate:
                pass
            else:
                if shortLeaveType:
                    ShortLeave(user = user,
                    short_leave_type = shortLeaveType,
                    for_date=checkdate,
                    status="open",
                    status_action_by = User.objects.get(id=35),
                    status_comments = reason,
                    due_date = dueDate,
                    reason = reason
                    ).save()


        else:
            print(user.first_name+user.last_name+" hr need to take care")
