from Leave.models import LeaveApplications
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

logger = logging.getLogger('MyANSRSource')

def previous_week_range(date):
    start_date = date + timedelta(-date.weekday(), weeks=-1)
    end_date = date + timedelta(-date.weekday() - 1)
    return start_date, end_date

# def previous_week_range(date):
#     start_date = date + timedelta(-date.weekday(), weeks=-1)
#     end_date = date + timedelta(-date.weekday() - 1)
#     return start_date, end_date

def dates_to_check_leave(start_date,end_date):
    dates = []
    delta = end_date - start_date

    for i in range(delta.days+1):
        dates.append(start_date + timedelta(days=i))
    return dates

class Command(BaseCommand):
    help = 'Daily leave Check.'

    def handle(self, *args, **options):
        daily_leave_check()

def getTime(t):
    return [t[:2],t[2:]]

def daily_leave_check():
    tzone = pytz.timezone('Asia/Kolkata')
    user_list = User.objects.filter(is_active=True)
    date = datetime.now().date()
    year = date.year
    week_dates = previous_week_range(date)
    start_date = week_dates[0]
    end_date = week_dates[1]
    dates = dates_to_check_leave(start_date, end_date)
    # print str(date) + " short attendance raised started running"
    FMT = '%H:%M:%S'
    holiday = Holiday.objects.all().values('date')
    dueDate = end_date + timedelta(days=12)
    fullDayOfficeStayTimeLimit = timedelta(hours=6, minutes=00, seconds=00)
    halfDayOfficeStayTimeLimit = timedelta(hours=3, minutes=00, seconds=00)
    for user in user_list:
        leaves = []
        for date in dates:
            hours_in_office = []
            leave_for_date = {}
            if date in [datedata['date'] for datedata in holiday] or date.weekday() >= 5:
                pass
            else:
                try:
                    leave = ""
                    employee = Employee.objects.filter(user_id=user.id)
                    appliedLeaveCheck = LeaveApplications.objects.filter(from_date__lte=date,
                                                                         to_date__gte=date,
                                                                         user=user.id,
                                                                         status__in=['open', 'approved'])
                    if employee:
                        attendance = Attendance.objects.filter(attdate=date,
                                                               incoming_employee_id=employee[0].employee_assigned_id)
                        if len(appliedLeaveCheck) >= 2:
                            for appliedleave in appliedLeaveCheck:
                                if appliedleave.leave_type_id == 16:
                                    temp_id = appliedleave.temp_id
                                    temp_attendance = Attendance.objects.filter(attdate=date,
                                                                                incoming_employee_id=temp_id)
                                    if temp_attendance:
                                        swipeIn = temp_attendance[0].swipe_in.astimezone(tzone)
                                        swipeOut = temp_attendance[0].swipe_out.astimezone(tzone)
                                        swipeInTime = swipeIn.strftime("%H:%M:%S")
                                        swipeOutTime = swipeOut.strftime("%H:%M:%S")
                                        tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime,
                                                                                                          FMT)
                                        hours_in_office.append(tdelta)
                                if appliedleave.leave_type_id != 16:
                                    if appliedleave.leave_type_id == 11:
                                        wfh = timedelta(hours=int(getTime(appliedleave.hours)[0]),
                                                        minutes=int(getTime(appliedleave.hours)[1]), seconds=00)
                                        hours_in_office.append(wfh)
                                if appliedleave.leave_type_id not in [11, 16]:
                                    if appliedleave.days_count == '0.5':
                                        tdelta = timedelta(hours=5, minutes=00, seconds=01)
                                    elif appliedleave.days_count == '1':
                                        tdelta = timedelta(hours=9, minutes=00, seconds=01)
                                    elif appliedleave.days_count > '1':
                                        leave_check = LeaveApplications.objects.filter(from_date__lte=date,
                                                                                       to_date__gte=date)
                                        if leave_check:
                                            tdelta = timedelta(hours=9, minutes=00, seconds=01)
                                    hours_in_office.append(tdelta)
                            if len(hours_in_office) > 2:
                                if (hours_in_office[0] + hours_in_office[1] + hours_in_office[2]) < halfDayOfficeStayTimeLimit:
                                    reason = "You had logged {0} hr that is below 3 hr".format(
                                        hours_in_office[0] + hours_in_office[1])
                                    leave = 'full_day'
                                elif (hours_in_office[0] + hours_in_office[1] + hours_in_office[2]) < fullDayOfficeStayTimeLimit:
                                    reason = "You had logged {0} hr that is below 6 hr".format(
                                        hours_in_office[0] + hours_in_office[1])
                                    leave = 'half_day'
                                if leave:
                                    leave_for_date['date'] = date
                                    leave_for_date['leave'] = leave
                                    leave_for_date['reason'] = reason
                                    leave_for_date['due_date'] = dueDate
                                    leaves.append(leave_for_date)
                            else:
                                if (hours_in_office[0] + hours_in_office[1]) < halfDayOfficeStayTimeLimit:
                                    reason = "You had logged {0} hr that is below 3 hr".format(
                                        hours_in_office[0] + hours_in_office[1])
                                    leave = 'full_day'
                                elif (hours_in_office[0] + hours_in_office[1]) < fullDayOfficeStayTimeLimit:
                                    reason = "You had logged {0} hr that is below 6 hr".format(
                                        hours_in_office[0] + hours_in_office[1])
                                    leave = 'half_day'
                                if leave:
                                    leave_for_date['date'] = date
                                    leave_for_date['leave'] = leave
                                    leave_for_date['reason'] = reason
                                    leave_for_date['due_date'] = dueDate
                                    leaves.append(leave_for_date)
                        elif appliedLeaveCheck and attendance:
                            if appliedLeaveCheck[0].leave_type_id == 11:
                                swipeIn = attendance[0].swipe_in.astimezone(tzone)
                                swipeOut = attendance[0].swipe_out.astimezone(tzone)
                                swipeInTime = swipeIn.strftime("%H:%M:%S")
                                swipeOutTime = swipeOut.strftime("%H:%M:%S")
                                tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                                wfh = timedelta(hours=int(getTime(appliedLeaveCheck[0].hours)[0]),
                                                minutes=int(getTime(appliedLeaveCheck[0].hours)[1]), seconds=00)
                                if tdelta + wfh < halfDayOfficeStayTimeLimit:
                                    reason = "You had logged {0} hr that is below 3 hr".format(tdelta + wfh)
                                    leave = 'full_day'
                                elif tdelta + wfh < fullDayOfficeStayTimeLimit:
                                    reason = "You had logged {0} hr that is below 6 hr".format(tdelta + wfh)
                                    leave = 'half_day'

                                if leave:
                                    leave_for_date['date'] = date
                                    leave_for_date['leave'] = leave
                                    leave_for_date['reason'] = reason
                                    leave_for_date['due_date'] = dueDate
                                    leaves.append(leave_for_date)
                            elif appliedLeaveCheck[0].leave_type_id != 11 and attendance:
                                leave_for_date = {}
                                swipeIn = attendance[0].swipe_in.astimezone(tzone)
                                swipeOut = attendance[0].swipe_out.astimezone(tzone)
                                swipeInTime = swipeIn.strftime("%H:%M:%S")
                                swipeOutTime = swipeOut.strftime("%H:%M:%S")
                                tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                                if appliedLeaveCheck[0].days_count == '0.5':
                                    app = timedelta(hours=04, minutes=30, seconds=00)
                                if tdelta + app < halfDayOfficeStayTimeLimit:
                                    reason = "You had logged {0} hr that is below 3 hr".format(tdelta + app)
                                    leave = 'full_day'
                                elif tdelta + app < fullDayOfficeStayTimeLimit:
                                    reason = "You had logged {0} hr that is below 6 hr".format(tdelta + app)
                                    leave = 'half_day'
                                if leave:
                                    leave_for_date['date'] = date
                                    leave_for_date['leave'] = leave
                                    leave_for_date['reason'] = reason
                                    leave_for_date['due_date'] = dueDate
                                    leaves.append(leave_for_date)
                            else:
                                swipeIn = attendance[0].swipe_in.astimezone(tzone)
                                swipeOut = attendance[0].swipe_out.astimezone(tzone)
                                swipeInTime = swipeIn.strftime("%H:%M:%S")
                                swipeOutTime = swipeOut.strftime("%H:%M:%S")
                                tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                                stayInTime = getTimeFromTdelta(tdelta, "{H:02}:{M:02}:{S:02}")
                                if tdelta < halfDayOfficeStayTimeLimit:
                                    reason = "You had logged {0} hr that is below 3 hr".format(stayInTime)
                                    leave = 'full_day'
                                elif tdelta < fullDayOfficeStayTimeLimit:
                                    reason = "You had logged {0} hr that is below 6 hr".format(stayInTime)
                                    leave = 'half_day'
                                if leave:
                                    leave_for_date['date'] = date
                                    leave_for_date['leave'] = leave
                                    leave_for_date['reason'] = reason
                                    leave_for_date['due_date'] = dueDate
                                    leaves.append(leave_for_date)
                        elif appliedLeaveCheck:
                            if appliedLeaveCheck[0].leave_type_id == 11 and not attendance:
                                tdelta = timedelta(hours=int(getTime(appliedLeaveCheck[0].hours)[0]),
                                                   minutes=int(getTime(appliedLeaveCheck[0].hours)[1]), seconds=00)
                                if tdelta < halfDayOfficeStayTimeLimit:
                                    reason = "full day leave"
                                    leave = 'full_day'
                                elif tdelta < fullDayOfficeStayTimeLimit:
                                    reason = "half day leave"
                                    leave = 'half_day'
                                if leave:
                                    leave_for_date['date'] = date
                                    leave_for_date['leave'] = leave
                                    leave_for_date['reason'] = reason
                                    leave_for_date['due_date'] = dueDate
                                    leaves.append(leave_for_date)
                            elif appliedLeaveCheck[0].leave_type_id == 16:
                                temp_id = appliedLeaveCheck[0].temp_id
                                temp_attendance = Attendance.objects.filter(attdate=date,
                                                                            incoming_employee_id=temp_id)
                                if temp_attendance:
                                    swipeIn = temp_attendance[0].swipe_in.astimezone(tzone)
                                    swipeOut = temp_attendance[0].swipe_out.astimezone(tzone)
                                    swipeInTime = swipeIn.strftime("%H:%M:%S")
                                    swipeOutTime = swipeOut.strftime("%H:%M:%S")
                                    tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                                    stayInTime = getTimeFromTdelta(tdelta, "{H:02}:{M:02}:{S:02}")
                                    if tdelta < halfDayOfficeStayTimeLimit:
                                        reason = "You had logged {0} hr that is below 3 hr".format(stayInTime)
                                        leave = 'full_day'
                                    elif tdelta < fullDayOfficeStayTimeLimit:
                                        reason = "You had logged {0} hr that is below 6 hr".format(stayInTime)
                                        leave = 'half_day'
                                    if leave:
                                        leave_for_date['date'] = date
                                        leave_for_date['leave'] = leave
                                        leave_for_date['reason'] = reason
                                        leave_for_date['due_date'] = dueDate
                                        leaves.append(leave_for_date)
                            elif appliedLeaveCheck[0].days_count == '0.5':
                                reason = "you had applied for only half day leave"
                                leave = 'half_day'
                                if leave:
                                    leave_for_date['date'] = date
                                    leave_for_date['leave'] = leave
                                    leave_for_date['reason'] = reason
                                    leave_for_date['due_date'] = dueDate
                                    leaves.append(leave_for_date)
                        elif attendance:
                            swipeIn = attendance[0].swipe_in.astimezone(tzone)
                            swipeOut = attendance[0].swipe_out.astimezone(tzone)
                            swipeInTime = swipeIn.strftime("%H:%M:%S")
                            swipeOutTime = swipeOut.strftime("%H:%M:%S")
                            tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                            stayInTime = getTimeFromTdelta(tdelta, "{H:02}:{M:02}:{S:02}")
                            if tdelta < halfDayOfficeStayTimeLimit:
                                reason = "You had logged {0} hr that is below 3 hr".format(stayInTime)
                                leave = 'full_day'
                                if leave:
                                    leave_for_date['date'] = date
                                    leave_for_date['leave'] = leave
                                    leave_for_date['reason'] = reason
                                    leave_for_date['due_date'] = dueDate
                                    leaves.append(leave_for_date)
                            elif tdelta < fullDayOfficeStayTimeLimit:
                                reason = "You had logged {0} hr that is below 6 hr".format(stayInTime)
                                leave = 'half_day'
                                if leave:
                                    leave_for_date['date'] = date
                                    leave_for_date['leave'] = leave
                                    leave_for_date['reason'] = reason
                                    leave_for_date['due_date'] = dueDate
                                    leaves.append(leave_for_date)
                        else:
                            swipeIn = datetime.now(pytz.timezone("Asia/Kolkata")) \
                                .replace(hour=0, minute=0, second=0, microsecond=0) \
                                .astimezone(pytz.utc)
                            swipeOut = datetime.now(pytz.timezone("Asia/Kolkata")) \
                                .replace(hour=0, minute=0, second=0, microsecond=0) \
                                .astimezone(pytz.utc)
                            swipeInTime = swipeIn.strftime("%H:%M:%S")
                            swipeOutTime = swipeOut.strftime("%H:%M:%S")
                            tdelta = timedelta(hours=0, minutes=0, seconds=0)
                            stayInTime = getTimeFromTdelta(tdelta, "{H:02}:{M:02}:{S:02}")
                            reason = "you were absent"
                            leave = 'full_day'
                            if len(appliedLeaveCheck) > 1:
                                pass
                            elif len(appliedLeaveCheck) == 1 and leave == 'half_day':
                                pass
                            elif len(appliedLeaveCheck) == 1 and appliedLeaveCheck[0].from_date == date and \
                                            appliedLeaveCheck[0].to_date == date and appliedLeaveCheck[
                                0].from_session == 'session_first' and appliedLeaveCheck[0].to_session == 'session_second':
                                pass
                            elif len(appliedLeaveCheck) == 1 and appliedLeaveCheck[0].from_date < date and \
                                            appliedLeaveCheck[0].to_date > date:
                                pass
                            elif len(appliedLeaveCheck) == 1 and appliedLeaveCheck[0].from_date == date and \
                                            appliedLeaveCheck[0].to_date > date and appliedLeaveCheck[
                                0].from_session == 'session_first':
                                pass
                            elif len(appliedLeaveCheck) == 1 and appliedLeaveCheck[0].from_date < date and \
                                            appliedLeaveCheck[
                                                0].to_date == date and appliedLeaveCheck[0].to_session == 'session_second':
                                pass
                            else:
                                if leave:
                                    leave_for_date['date'] = date
                                    leave_for_date['leave'] = leave
                                    leave_for_date['reason'] = reason
                                    leave_for_date['due_date'] = dueDate
                                    leaves.append(leave_for_date)
                    else:
                        print(user.first_name + user.last_name + " hr need to take care")
                except:
                    logger.debug("missing records")
        if leaves:
            try:
                send_mail(user, leaves, dates, reason, "open")
            except:
                logger.debug('email send issue user id' + user.id)
    print str(datetime.now()) + " Daily leave check raised finished running"

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

def send_mail(user, leavetype, fordate, status_comments, status):
    msg_html = render_to_string('email_templates/short_attendance_raised.html',
                                {'registered_by': user.first_name,
                                 'leaveType': leavetype,
                                 'fordate': fordate,
                                 'reason': status_comments,
                                 'status': status,
                                 })

    mail_obj = EmailMessage('Daily leave check',
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