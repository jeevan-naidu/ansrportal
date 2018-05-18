from Leave.models import ShortAttendance, LeaveApplications, LeaveSummary, LeaveType
from employee.models import Attendance,Employee
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta, time
from django.core.management.base import BaseCommand
from CompanyMaster.models import Holiday
import logging
import pytz
from string import Formatter
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from Leave.tasks import leaveTypeDictionary

logger = logging.getLogger('MyANSRSource')

currentTime = datetime.now().date().strftime('%Y-%m-%d %H:%M:%S')
fileName = " Daily Leave Deduction " + str(currentTime) + ".csv"
print(fileName)
writeFile = open(fileName, "w+")

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
    help = 'Weekly leave deduction.'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)
        parser.add_argument('month', type=int)
        parser.add_argument('day', type=int)

    def handle(self, *args, **options):
        weekly_leave_deduction(options['year'], options['month'], options['day'])

def getTime(t):
    return [t[:2],t[2:]]

def weekly_leave_deduction(year, month, day):
    tzone = pytz.timezone('Asia/Kolkata')
    user_list = User.objects.filter(is_active=True)
    date = datetime(year, month, day)
    start_date = date.date()
    end_date = start_date + timedelta(days=4)
    dates = dates_to_check_leave(start_date, end_date)
    holiday = Holiday.objects.all().values('date')
    # print str(date) + " short attendance raised started running"
    FMT = '%H:%M:%S'
    dueDate = end_date + timedelta(days=7)
    fullDayOfficeStayTimeLimit = timedelta(hours=6, minutes=00, seconds=00)
    halfDayOfficeStayTimeLimit = timedelta(hours=3, minutes=00, seconds=00)
    for user in user_list:
        leaves = []
        dates_av = []
        leave_for_date = {}
        employee_attendance = []
        for date in dates:
            if date in [datedata['date'] for datedata in holiday]:
                employee_attendance.append(timedelta(hours=9, minutes=00, seconds=00))
                pass
            elif date.weekday() >= 5:
                pass
            else:
                try:
                    dates_av.append(date)
                    employee = Employee.objects.filter(user_id=user.id)
                    appliedLeaveCheck = LeaveApplications.objects.filter(from_date__lte=date,
                                                                         to_date__gte=date,
                                                                         user=user.id,
                                                                         status__in=['open', 'approved'])
                    for leave in appliedLeaveCheck:
                        if leave.from_date == leave.to_date and leave.leave_type_id not in [16,11]:
                            dates_av.remove(date)
                        else:
                            leave_dates = dates_to_check_leave(leave.from_date,leave.to_date)
                            for leave_date in leave_dates:
                                if leave_date in dates_av:
                                    dates_av.remove(leave_date)
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
                                        employee_attendance.append(tdelta)
                                if appliedleave.leave_type_id != 16:
                                    if appliedleave.leave_type_id == 11:
                                        wfh = timedelta(hours=int(getTime(appliedleave.hours)[0]),
                                                        minutes=int(getTime(appliedleave.hours)[1]), seconds=00)
                                        employee_attendance.append(wfh)
                                if appliedleave.leave_type_id not in [11, 16]:
                                    if appliedleave.days_count == '0.5':
                                        employee_attendance.append(timedelta(hours=5, minutes=00, seconds=01))
                                    elif appliedleave.days_count == '1':
                                        employee_attendance.append(timedelta(hours=9, minutes=00, seconds=01))
                                    elif appliedleave.days_count > '1':
                                        leave_check = LeaveApplications.objects.filter(from_date__lte=date,
                                                                                       to_date__gte=date)
                                        if leave_check:
                                            employee_attendance.append(timedelta(hours=9, minutes=00, seconds=01))
                            if attendance:
                                swipeIn = attendance[0].swipe_in.astimezone(tzone)
                                swipeOut = attendance[0].swipe_out.astimezone(tzone)
                                swipeInTime = swipeIn.strftime("%H:%M:%S")
                                swipeOutTime = swipeOut.strftime("%H:%M:%S")
                                tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                                stayInTime = getTimeFromTdelta(tdelta, "{H:02}:{M:02}:{S:02}")
                                employee_attendance.append(tdelta)
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
                                    employee_attendance.append(tdelta)
                                if attendance:
                                    swipeIn = attendance[0].swipe_in.astimezone(tzone)
                                    swipeOut = attendance[0].swipe_out.astimezone(tzone)
                                    swipeInTime = swipeIn.strftime("%H:%M:%S")
                                    swipeOutTime = swipeOut.strftime("%H:%M:%S")
                                    tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                                    stayInTime = getTimeFromTdelta(tdelta, "{H:02}:{M:02}:{S:02}")
                                    employee_attendance.append(tdelta)
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
                                employee_attendance.append(tdelta+wfh)
                            elif appliedLeaveCheck[0].leave_type_id != 11 and attendance:
                                leave_for_date = {}
                                swipeIn = attendance[0].swipe_in.astimezone(tzone)
                                swipeOut = attendance[0].swipe_out.astimezone(tzone)
                                swipeInTime = swipeIn.strftime("%H:%M:%S")
                                swipeOutTime = swipeOut.strftime("%H:%M:%S")
                                tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                                if appliedLeaveCheck[0].days_count == '0.5':
                                    app = (timedelta(hours=5, minutes=00, seconds=01))
                                elif appliedLeaveCheck[0].days_count == '1':
                                    app = (timedelta(hours=9, minutes=00, seconds=01))
                                elif appliedLeaveCheck[0].days_count > '1':
                                    leave_check = LeaveApplications.objects.filter(from_date__lte=date,
                                                                                   to_date__gte=date)
                                    if leave_check:
                                        app = (timedelta(hours=9, minutes=00, seconds=01))
                                timediff = tdelta + app
                                employee_attendance.append(timediff)
                            else:
                                swipeIn = attendance[0].swipe_in.astimezone(tzone)
                                swipeOut = attendance[0].swipe_out.astimezone(tzone)
                                swipeInTime = swipeIn.strftime("%H:%M:%S")
                                swipeOutTime = swipeOut.strftime("%H:%M:%S")
                                tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                                stayInTime = getTimeFromTdelta(tdelta, "{H:02}:{M:02}:{S:02}")
                                employee_attendance.append(tdelta)
                        elif appliedLeaveCheck:
                            if appliedLeaveCheck[0].leave_type_id == 11 and not attendance:
                                tdelta = timedelta(hours=int(getTime(appliedLeaveCheck[0].hours)[0]),
                                                   minutes=int(getTime(appliedLeaveCheck[0].hours)[1]), seconds=00)
                                employee_attendance.append(tdelta)
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
                                    employee_attendance.append(tdelta)
                            elif appliedLeaveCheck[0].days_count == '0.5':
                                employee_attendance.append(timedelta(hours=5, minutes=00, seconds=01))
                            elif appliedLeaveCheck[0].days_count == '1':
                                employee_attendance.append(timedelta(hours=9, minutes=00, seconds=01))
                            elif appliedLeaveCheck[0].days_count > '1':
                                leave_check = LeaveApplications.objects.filter(from_date__lte=date,
                                                                               to_date__gte=date)
                                if leave_check:
                                    employee_attendance.append(timedelta(hours=9, minutes=00, seconds=01))
                        elif attendance:
                            swipeIn = attendance[0].swipe_in.astimezone(tzone)
                            swipeOut = attendance[0].swipe_out.astimezone(tzone)
                            swipeInTime = swipeIn.strftime("%H:%M:%S")
                            swipeOutTime = swipeOut.strftime("%H:%M:%S")
                            tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                            stayInTime = getTimeFromTdelta(tdelta, "{H:02}:{M:02}:{S:02}")
                            employee_attendance.append(tdelta)
                        else:
                            employee_attendance.append(timedelta(hours=0, minutes=00, seconds=01))
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
        total_sec = sum(employee_attendance,timedelta()).seconds + sum(employee_attendance,timedelta()).days * 24 * 3600
        total_time =  float(u"{0}.{1}".format(total_sec // 3600,
                                (total_sec % 3600) // 60))
        print total_time, user
        if employee_attendance:
            try:
                if 39.5 <= total_time < 44:
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 45 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'half_day'
                    leave_for_date['date'] = dates_av[0]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 35 <= total_time < 39.5:
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 40 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[0]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 30.5 <= total_time < 35:
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 35 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 35 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'half_day'
                    leave_for_date['date'] = dates_av[1]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 26 <= total_time < 30.5:
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 30.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 30.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[1]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 21.5 <= total_time < 26:
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 26 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 26 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[1]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 26 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'half_day'
                    leave_for_date['date'] = dates_av[2]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 17 <= total_time < 21.5:
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 21.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 21.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[1]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 21.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[2]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 12.5 <= total_time < 17:
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 17.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 17.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[1]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 17.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[2]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 17.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'half_day'
                    leave_for_date['date'] = dates_av[3]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 9 <= total_time < 12.5:
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 12.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 12.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[1]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 12.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[2]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 12.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[3]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 4.5 <= total_time < 9:
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 9 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 9 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[1]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 9 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[2]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 9 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[3]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 9 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'half_day'
                    leave_for_date['date'] = dates_av[4]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 0 <= total_time < 4.5:
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 4.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 4.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[1]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 4.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[2]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 4.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[3]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "You had logged " + str(total_time) + " hr that is below 4.5 hr"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates_av[4]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
            except:
                logger.debug('email send issue user id' + user.id)
    print str(datetime.now()) + " Weekly leave deduction finished running"

def applyLeave(user, leaves, year):
    for leave in leaves:
        user_id = user.id
        reason = "applied by system"
        applied_by = User.objects.get(id=35).id
        avaliable_leave = avaliableLeaveCheck(user_id, leave, year)
        if avaliable_leave != 0:
            try:
                if len(avaliable_leave) >= 2:
                    for leave_ty in avaliable_leave:
                        leave_type = LeaveSummary.objects.get(user=user_id, leave_type=leave_ty, year=year)
                        if leavecheckonautoapplydate(leave, user_id):
                            leave['leave'] = 'half_day'
                            leavesubmit(leave, leave_type, user_id, applied_by)
                if len(avaliable_leave) == 1:
                    avaliable_leave.append(0)
                    for leave_ty in avaliable_leave:
                        if leave_ty != 0:
                            leave_type = LeaveSummary.objects.get(user=user_id, leave_type=leave_ty, year=year)
                            if leavecheckonautoapplydate(leave, user_id):
                                leave['leave'] = 'half_day'
                                leavesubmit(leave, leave_type, user_id, applied_by)
                        else:
                            leave_type, created = LeaveSummary.objects.get_or_create(user=User.objects.get(id=user_id),
                                                                                     leave_type=LeaveType.objects.get(
                                                                                         leave_type='loss_of_pay'),
                                                                                     applied=0, approved=0,
                                                                                     balance=0,
                                                                                     year=year)
                            if leavecheckonautoapplydate(leave, user_id):
                                leave['leave'] = 'half_day'
                                leavesubmit(leave, leave_type, user_id, applied_by)

            except:
                leave_type = LeaveSummary.objects.get(user=user_id,leave_type=avaliable_leave,year=year)
                if leavecheckonautoapplydate(leave, user_id):
                    leavesubmit(leave, leave_type, user_id, applied_by)
        else:
            leave_type = LeaveSummary.objects.filter(user=user_id,
                                             leave_type__leave_type='loss_of_pay',
                                             year=year)
            if leave_type:
                leave_type = leave_type[0]
            else:
                leave_type, created = LeaveSummary.objects.get_or_create(user=User.objects.get(id=user_id),
                                            leave_type=LeaveType.objects.get(leave_type='loss_of_pay'),
                                            applied=0, approved=0,
                                            balance=0,
                                            year=year)
            if leavecheckonautoapplydate(leave, user_id):
                leavesubmit(leave, leave_type, user_id, applied_by)

def leavecheckonautoapplydate(leave, user):
    leave_check = LeaveApplications.objects.filter(from_date__gte=leave['date'],
                                             to_date__lte=leave['date'],
                                             user=user)
    if leave_check:
        if leave_check[0].hours:
            wfh = timedelta(hours=int(getTime(leave_check[0].hours)[0]),
                            minutes=int(getTime(leave_check[0].hours)[1]), seconds=00)
            fullDayOfficeStayTimeLimit = timedelta(hours=6, minutes=00, seconds=00)
            halfDayOfficeStayTimeLimit = timedelta(hours=3, minutes=00, seconds=00)
            if wfh < halfDayOfficeStayTimeLimit:
                return True
            elif wfh < fullDayOfficeStayTimeLimit:
                return True
    if leave_check:
        if leave_check[0].days_count == '0.5':
            return True
        if leave_check[0].days_count == '1':
            return True
    if leave_check and \
                    len(leave_check) > 1 or\
                    leave['leave'] == 'half_day' and leave_check or leave_check and\
                            leave_check[0].from_session == 'session_first'\
            and leave_check[0].to_session == 'session_second':
        return False
    else:
        return True

def avaliableLeaveCheck(user_id, short_leave_type, year):
    leavesavaliableforapply = ['casual_leave', 'earned_leave']
    leave_type_combined = []
    for val in leavesavaliableforapply:
        leaveapp = LeaveSummary.objects.filter(user=user_id, leave_type__leave_type=val, year=year)
        if short_leave_type['leave'] == 'full_day' and leaveapp and float(leaveapp[0].balance.encode('utf-8')) >= 1:
            if leave_type_combined:
                leave_type_combined.append(leaveapp[0].leave_type)
            else:
                return leaveapp[0].leave_type
        elif short_leave_type['leave'] == 'full_day' and leaveapp and float(leaveapp[0].balance.encode('utf-8')) > 0.5:
            return leaveapp[0].leave_type
        elif short_leave_type['leave'] == 'full_day' and leaveapp and float(leaveapp[0].balance.encode('utf-8')) >= 0.5:
            leave_type_combined.append(leaveapp[0].leave_type)
        elif short_leave_type['leave'] == 'half_day' and leaveapp and float(leaveapp[0].balance.encode('utf-8')) >= 0.5:
            return leaveapp[0].leave_type
        elif leaveapp and leaveapp and float(leaveapp[0].balance.encode('utf-8')) > 0.5:
            return leaveapp[0].leave_type
    if short_leave_type['leave'] == 'full_day' and len(leave_type_combined) >= 1:
        return leave_type_combined
    return 0

def leavesubmit(leave, leave_type,  user_id, applied_by):
    try:
        leaveapp = LeaveApplications.objects.filter(from_date__lte=leave['date'],
                                                 to_date__gte=leave['date'],
                                                 user=user_id,
                                                    status__in=['open', 'approved'])
        if leaveapp and leave['leave'] == 'full_day' and leaveapp[0].leave_type_id not in [16, 11]:
            leavecount = .5
            if leaveapp[0].from_session == 'session_first':
                fromsession = 'session_second'
                tosession = 'session_second'
            else:
                fromsession = 'session_first'
                tosession = 'session_first'
        elif leave['leave'] == 'full_day':
            leavecount = 1
            fromsession = 'session_first'
            tosession = 'session_second'
        else:
            leavecount = .5
            fromsession = 'session_first'
            tosession = 'session_first'
        leave_type.balance = float(leave_type.balance) - leavecount
        leave_type.approved = float(leave_type.approved) + leavecount
        manager_id = Employee.objects.filter(user_id=user_id).values('manager_id')
        manager = Employee.objects.filter(employee_assigned_id=manager_id).values('user_id')
        manager_d = User.objects.get(id=manager[0]['user_id'])
        applied_by = User.objects.get(id=applied_by)
        LeaveApplications(user=User.objects.get(id=user_id),
                          leave_type=leave_type.leave_type,
                          from_date=leave['date'],
                          to_date=leave['date'],
                          from_session=fromsession,
                          to_session=tosession,
                          days_count=leavecount, reason=leave['reason'],
                          status='approved',
                          status_action_by=applied_by,
                          applied_by=applied_by,
                          apply_to=manager_d,
                          ).save()
        leave_type.save()
        send_mail(User.objects.get(id=user_id),
                  leave_type.leave_type.leave_type,
                  leave['date'],
                  leave['date'],
                  leavecount)
        writeFile.write(
            "'{0}','{1}','{2}','{3}','{4}'".format(str(User.objects.get(id=user_id)), str(manager_d),
                                                   str(leave['leave']), str(leave['reason']), str(leave['date'])))
        writeFile.write("\n")

    except:
        print "please check manager for user id {0}".format(user_id)
        # logger.error("error happen for {0} while putting forced leave manager is not there".format(user_id))

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

def send_mail(user, leavetype, fromdate, todate, count):
    msg_html = render_to_string('email_templates/weekly-leave_deduction.html',
                                {'registered_by': user.first_name,
                                 'leaveType': leavetype,
                                 'fromdate': fromdate,
                                 'todate': todate,
                                 'count': count,
                                 })

    mail_obj = EmailMessage('Leave Deduction',
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