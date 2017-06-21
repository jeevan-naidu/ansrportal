from Leave.models import ShortAttendance, LeaveApplications
from employee.models import Attendance,Employee
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta, time
from django.core.management.base import BaseCommand
import logging
import pytz
from string import Formatter
from CompanyMaster.models import Holiday
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from Leave.tasks import shortattendancetype

logger = logging.getLogger('MyANSRSource')


class Command(BaseCommand):
    help = 'Upload Leave summary for new joinee.'

    def handle(self, *args, **options):
        shortLeave()


def shortLeave():
    print str(datetime.now()) + " short attendance raised started running"
    tzone = pytz.timezone('Asia/Kolkata')
    user_list = User.objects.filter(is_active=True)
    checkdate = date.today() - timedelta(days=4)
    FMT = '%H:%M:%S'
    holiday = Holiday.objects.all().values('date')
    dueDate = checkdate + timedelta(days=30)
    morningInTimeLimit = datetime.strptime("10:15:00", FMT)
    fullDayOfficeStayTimeLimit = timedelta(hours=8, minutes=50, seconds=00)
    halfDayOfficeStayTimeLimit = timedelta(hours=4, minutes=30, seconds=00)
    if checkdate in [datedata['date'] for datedata in holiday] or checkdate.weekday() >= 5:
        return

    for user in user_list:
        try:
            reason = ""
            shortLeaveType = ""
            employee = Employee.objects.filter(user_id = user.id)
            appliedLeaveCheck = LeaveApplications.objects.filter(from_date__lte=checkdate,
                                                                 to_date__gte=checkdate,
                                                                 user=user.id,
                                                                 status__in=['open', 'approved'])
            manager_id = Employee.objects.filter(user_id=user).values('manager_id')
            manager = Employee.objects.filter(employee_assigned_id=manager_id).values('user_id')
            if manager:
                manager_d = User.objects.get(id=manager[0]['user_id'])
            else:
                manager_d = User.objects.get(id= 35)
            if employee:
                attendance = Attendance.objects.filter(attdate=checkdate, employee_id=employee[0].employee_assigned_id)
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
                    # elif morningInTime > morningInTimeLimit:
                    #     reason = "you came at {0}, you came late".format(morningInTime.time().isoformat())
                    #     shortLeaveType = 'half_day'
                else:
                    swipeIn = datetime.now(pytz.timezone("Asia/Kolkata"))\
                        .replace(hour=0, minute=0, second=0, microsecond=0)\
                        .astimezone(pytz.utc)
                    swipeOut = datetime.now(pytz.timezone("Asia/Kolkata"))\
                        .replace(hour=0, minute=0, second=0, microsecond=0)\
                        .astimezone(pytz.utc)
                    swipeInTime = swipeIn.strftime("%H:%M:%S")
                    swipeOutTime = swipeOut.strftime("%H:%M:%S")
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
                        ShortAttendance.objects.get_or_create(user=user, short_leave_type=shortLeaveType,
                                                              for_date=checkdate,
                                                              status="open",
                                                              status_action_by=User.objects.get(id=35),
                                                              status_comments=reason,
                                                              due_date=dueDate,
                                                              dispute="open",
                                                              reason=reason,
                                                              stay_time=stayInTime,
                                                              apply_to=manager_d,
                                                              swipe_in=swipeInTime,
                                                              swipe_out=swipeOutTime
                                                              )
                        try:
                            send_mail(user, shortLeaveType, checkdate, dueDate, reason, "open")
                        except:
                            logger.debug('email send issue user id' + user.id)

            else:
                print(user.first_name + user.last_name + " hr need to take care")
        except:
            ShortAttendance.objects.get_or_create(user=user,
                                                  short_leave_type='full_day',
                                                  for_date=checkdate,
                                                  status="open",
                                                  status_action_by=User.objects.get(id=35),
                                                  status_comments="missing record",
                                                  due_date=dueDate,
                                                  dispute="open",
                                                  reason="missing records",
                                                  apply_to=manager_d,
                                                  swipe_in=time(00, 00, 00),
                                                  swipe_out=time(00, 00, 00),
                                                  stay_time=time(00, 00, 00),
                                                  )
            send_mail(user, 'full_day', checkdate, dueDate, "missing records", "open")
    print str(datetime.now()) + " short attendance raised finished running"






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


def send_mail(user, leavetype, fordate, duedate, status_comments, status):
    msg_html = render_to_string('email_templates/short_attendance_raised.html',
                                {'registered_by': user.first_name,
                                 'leaveType': shortattendancetype[leavetype],
                                 'fordate': fordate,
                                 'duedate': duedate,
                                 'reason': status_comments,
                                 'status': status,
                                 })

    mail_obj = EmailMessage('Short Attendance Raised',
                            msg_html, settings.EMAIL_HOST_USER, [user.email],
                            cc=[])

    mail_obj.content_subtype = 'html'
    email_status = mail_obj.send()
    if email_status == 0:
        logger.error(
            "Unable To send Mail To The Authorities For"
            "The Following Leave Applicant : Date time : ")
        return "failed"
    else:
        logger.debug('send successful')