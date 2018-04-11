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

# def previous_week_range(date):
#     week_dates = []
#     for week_no in [2]:
#         start_date = date + timedelta(-date.weekday(), weeks=-week_no)
#         end_date = date + timedelta(-date.weekday() - 1)
#         week_dates.append(start_date)
#         week_dates.append(end_date)
#     return week_dates

def previous_week_range(date):
    start_date = date + timedelta(-date.weekday(), weeks=-1)
    end_date = date + timedelta(-date.weekday() - 1)
    return start_date, end_date

def dates_to_check_leave(start_date,end_date):
    dates = []
    delta = end_date - start_date

    for i in range(delta.days+1):
        dates.append(start_date + timedelta(days=i))
    return dates

class Command(BaseCommand):
    help = 'Weekly leave Check.'

    def handle(self, *args, **options):
        daily_leave_check()

def getTime(t):
    return [t[:2],t[2:]]

def daily_leave_check(year, month, day):
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
        employee_attendance = []
        for date in dates:
            if date in [datedata['date'] for datedata in holiday]:
                employee_attendance.append(9)
                pass
            elif date.weekday() >= 5:
                pass
            else:
                try:
                    employee = Employee.objects.filter(user_id=user.id)
                    appliedLeaveCheck = LeaveApplications.objects.filter(from_date__lte=date,
                                                                         to_date__gte=date,
                                                                         user=user.id,
                                                                         status__in=['open', 'approved'])
                    if employee:
                        attendance = Attendance.objects.filter(attdate=date,
                                                               incoming_employee_id=employee[0].employee_assigned_id)
                        # import ipdb; ipdb.set_trace()
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
                                        timediff = tdelta
                                        atttime = u"{0}.{1}".format(timediff.seconds // 3600,
                                                                    (timediff.seconds % 3600) // 60)
                                        employee_attendance.append(float(atttime))
                                if appliedleave.leave_type_id != 16:
                                    if appliedleave.leave_type_id == 11:
                                        wfh = timedelta(hours=int(getTime(appliedleave.hours)[0]),
                                                        minutes=int(getTime(appliedleave.hours)[1]), seconds=00)

                                        timediff = wfh
                                        atttime = u"{0}.{1}".format(timediff.seconds // 3600,
                                                                    (timediff.seconds % 3600) // 60)
                                        employee_attendance.append(float(atttime))
                                if appliedleave.leave_type_id not in [11, 16]:
                                    if appliedleave.days_count == '0.5':
                                        tdelta = timedelta(hours=04, minutes=30, seconds=00)
                                        timediff = tdelta
                                        atttime = u"{0}.{1}".format(timediff.seconds // 3600,
                                                                    (timediff.seconds % 3600) // 60)
                                        employee_attendance.append(float(atttime))
                        elif appliedLeaveCheck and attendance:
                            if appliedLeaveCheck[0].leave_type_id == 16:
                                temp_id = appliedLeaveCheck[0].temp_id
                                temp_attendance = Attendance.objects.filter(attdate=date,
                                                                            incoming_employee_id=temp_id)
                                if temp_attendance:
                                    swipeIn = temp_attendance[0].swipe_in.astimezone(tzone)
                                    swipeOut = temp_attendance[0].swipe_out.astimezone(tzone)
                                    swipeInTime = swipeIn.strftime("%H:%M:%S")
                                    swipeOutTime = swipeOut.strftime("%H:%M:%S")
                                    tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime,
                                                                                                      FMT)
                                    timediff = tdelta
                                    atttime = u"{0}.{1}".format(timediff.seconds // 3600,
                                                                (timediff.seconds % 3600) // 60)
                                    employee_attendance.append(float(atttime))
                                if attendance:
                                    swipeIn = attendance[0].swipe_in.astimezone(tzone)
                                    swipeOut = attendance[0].swipe_out.astimezone(tzone)
                                    swipeInTime = swipeIn.strftime("%H:%M:%S")
                                    swipeOutTime = swipeOut.strftime("%H:%M:%S")
                                    tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                                    stayInTime = getTimeFromTdelta(tdelta, "{H:02}:{M:02}:{S:02}")
                                    timediff = tdelta
                                    atttime = u"{0}.{1}".format(timediff.seconds // 3600,
                                                                (timediff.seconds % 3600) // 60)
                                    employee_attendance.append(float(atttime))
                            elif appliedLeaveCheck[0].leave_type_id == 11:
                                swipeIn = attendance[0].swipe_in.astimezone(tzone)
                                swipeOut = attendance[0].swipe_out.astimezone(tzone)
                                swipeInTime = swipeIn.strftime("%H:%M:%S")
                                swipeOutTime = swipeOut.strftime("%H:%M:%S")
                                tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(
                                    swipeInTime, FMT)
                                wfh = timedelta(hours=int(getTime(appliedLeaveCheck[0].hours)[0]),
                                                minutes=int(getTime(appliedLeaveCheck[0].hours)[1]),
                                                seconds=00)
                                timediff = wfh
                                atttime = u"{0}.{1}".format(timediff.seconds // 3600,
                                                            (timediff.seconds % 3600) // 60)
                                employee_attendance.append(float(atttime))
                            elif appliedLeaveCheck[0].leave_type_id != 11 and attendance:
                                leave_for_date = {}
                                swipeIn = attendance[0].swipe_in.astimezone(tzone)
                                swipeOut = attendance[0].swipe_out.astimezone(tzone)
                                swipeInTime = swipeIn.strftime("%H:%M:%S")
                                swipeOutTime = swipeOut.strftime("%H:%M:%S")
                                tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                                if appliedLeaveCheck[0].days_count == '0.5':
                                    app = timedelta(hours=04, minutes=30, seconds=00)
                                timediff = tdelta + app
                                atttime = u"{0}.{1}".format(timediff.seconds // 3600,
                                                            (timediff.seconds % 3600) // 60)
                                employee_attendance.append(float(atttime))
                            else:
                                swipeIn = attendance[0].swipe_in.astimezone(tzone)
                                swipeOut = attendance[0].swipe_out.astimezone(tzone)
                                swipeInTime = swipeIn.strftime("%H:%M:%S")
                                swipeOutTime = swipeOut.strftime("%H:%M:%S")
                                tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                                stayInTime = getTimeFromTdelta(tdelta, "{H:02}:{M:02}:{S:02}")
                                timediff = tdelta
                                atttime = u"{0}.{1}".format(timediff.seconds // 3600,
                                                            (timediff.seconds % 3600) // 60)
                                employee_attendance.append(float(atttime))
                        elif appliedLeaveCheck:
                            if appliedLeaveCheck[0].leave_type_id == 11 and not attendance:
                                tdelta = timedelta(hours=int(getTime(appliedLeaveCheck[0].hours)[0]),
                                                   minutes=int(getTime(appliedLeaveCheck[0].hours)[1]), seconds=00)
                                timediff = tdelta
                                atttime = u"{0}.{1}".format(timediff.seconds // 3600,
                                                            (timediff.seconds % 3600) // 60)
                                employee_attendance.append(float(atttime))
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
                                    timediff = tdelta
                                    atttime = u"{0}.{1}".format(timediff.seconds // 3600,
                                                                (timediff.seconds % 3600) // 60)
                                    employee_attendance.append(float(atttime))
                            elif appliedLeaveCheck[0].days_count == '0.5':
                                employee_attendance.append(4.5)
                        elif attendance:
                            swipeIn = attendance[0].swipe_in.astimezone(tzone)
                            swipeOut = attendance[0].swipe_out.astimezone(tzone)
                            swipeInTime = swipeIn.strftime("%H:%M:%S")
                            swipeOutTime = swipeOut.strftime("%H:%M:%S")
                            tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                            stayInTime = getTimeFromTdelta(tdelta, "{H:02}:{M:02}:{S:02}")
                            timediff = tdelta
                            atttime = u"{0}.{1}".format(timediff.seconds // 3600,
                                                        (timediff.seconds % 3600) // 60)
                            employee_attendance.append(float(atttime))
                        else:
                            employee_attendance.append(0)
                        if  len(appliedLeaveCheck)>1:
                            pass
                        elif len(appliedLeaveCheck)==1 and appliedLeaveCheck[0].from_date==date and appliedLeaveCheck[0].to_date==date and appliedLeaveCheck[0].from_session=='session_first' and appliedLeaveCheck[0].to_session== 'session_second':
                            pass
                        elif len(appliedLeaveCheck)==1 and appliedLeaveCheck[0].from_date<date and appliedLeaveCheck[0].to_date>date:
                            pass
                        elif len(appliedLeaveCheck)==1 and appliedLeaveCheck[0].from_date==date and appliedLeaveCheck[0].to_date>date and appliedLeaveCheck[0].from_session=='session_first':
                            pass
                        elif len(appliedLeaveCheck) == 1 and appliedLeaveCheck[0].from_date < date and appliedLeaveCheck[
                            0].to_date == date and appliedLeaveCheck[0].to_session== 'session_second':
                            pass
                    else:
                        print(user.first_name + user.last_name + " hr need to take care")
                except:
                    logger.debug("missing records")
        if employee_attendance:
            try:
                if 39.5 < sum(employee_attendance) < 44:
                    reason = "you had put " + str(sum(employee_attendance)) + " hours which is below 44 hours"
                    leave = 'half_day'
                    send_mail(user, sum(employee_attendance), leave, dates[0], dates[-1], dueDate, reason, "open")
                elif 35 < sum(employee_attendance) < 39.5:
                    reason = "you had put " + str(sum(employee_attendance)) + " hours which is below 39.5 hours"
                    leave = 'full_day'
                    send_mail(user, sum(employee_attendance), leave, dates[0], dates[-1], dueDate, reason, "open")
                elif 30.5 < sum(employee_attendance) < 35:
                    reason = "you had put " + str(sum(employee_attendance)) + " hours which is below 35 hours"
                    leave = '1.5'
                    send_mail(user, sum(employee_attendance), leave, dates[0], dates[-1], dueDate, reason, "open")
                elif 26 < sum(employee_attendance) < 30.5:
                    reason = "you had put " + str(sum(employee_attendance)) + " hours which is below 30.5 hours"
                    leave = '2'
                    send_mail(user, sum(employee_attendance), leave, dates[0], dates[-1], dueDate, reason, "open")
                elif 21.5 < sum(employee_attendance) < 26:
                    reason = "you had put " + str(sum(employee_attendance)) + " hours which is below 26 hours"
                    leave = '2.5'
                    send_mail(user, sum(employee_attendance), leave, dates[0], dates[-1], dueDate, reason, "open")
                elif 17 < sum(employee_attendance) < 21.5:
                    reason = "you had put " + str(sum(employee_attendance)) + " hours which is below 21.5 hours"
                    leave = '3'
                    send_mail(user, sum(employee_attendance), leave, dates[0], dates[-1], dueDate, reason, "open")
                elif 12.5 < sum(employee_attendance) < 17:
                    reason = "you had put " + str(sum(employee_attendance)) + " hours which is below 17.5 hours"
                    leave = '3.5'
                    send_mail(user, sum(employee_attendance), leave, dates[0], dates[-1], dueDate, reason, "open")
                elif 9 < sum(employee_attendance) < 12.5:
                    reason = "you had put " + str(sum(employee_attendance)) + " hours which is below 12.5 hours"
                    leave = '4'
                    send_mail(user, sum(employee_attendance), leave, dates[0], dates[-1], dueDate, reason, "open")
                elif 4.5 < sum(employee_attendance) < 9:
                    reason = "you had put " + str(sum(employee_attendance)) + " hours which is below 9 hours"
                    leave = '4.5'
                    send_mail(user, sum(employee_attendance), leave, dates[0], dates[-1], dueDate, reason, "open")
                elif 0 < sum(employee_attendance) < 4.5:
                    reason = "you had put " + str(sum(employee_attendance)) + " hours which is below 4.5 hours"
                    leave = '5'
                    send_mail(user, sum(employee_attendance), leave, dates[0], dates[-1], dueDate,  reason, "open")
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

def send_mail(user, total_hours, leavetype, from_date, to_date, dueDate, status_comments, status):
    msg_html = render_to_string('email_templates/weekly_check.html',
                                {'registered_by': user.first_name,
                                 'total_hours' : total_hours,
                                 'leaveType': leavetype,
                                 'from_date': from_date,
                                 'to_date': to_date,
                                 'dueDate': dueDate,
                                 'reason': status_comments,
                                 'status': status,
                                 })

    mail_obj = EmailMessage('Weekly check',
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