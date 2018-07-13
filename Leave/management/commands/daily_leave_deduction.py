from Leave.models import ShortAttendance, LeaveApplications, LeaveSummary, LeaveType
from employee.models import Attendance, Employee
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta, time
from django.core.management.base import BaseCommand
from CompanyMaster.models import Holiday
import logging
import os
import pytz
from string import Formatter
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from Leave.tasks import leaveTypeDictionary

logger = logging.getLogger('MyANSRSource')

currentTime = datetime.now().date().strftime('%Y_%m_%d_%H_%M_%S')
fileName = "DailyLeaveDeduction" + str(currentTime) + ".csv"
print(fileName)
writeFile = open(fileName, "w+")
writeFile.write("Employee, Employee ID, Manager, Manager Id, Leave, Reason, Date \n")

writeFileemail = open("dailydeduction.csv", "w+")
writeFileemail.write("Employee, Employee ID, Manager, Manager Id, Leave, Reason, Date, Leave Type, Employee Email, Manager Email, Deduction Type\n")

class Command(BaseCommand):
    help = 'Upload Leave summary for new joinee.'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)
        parser.add_argument('month', type=int)
        parser.add_argument('day', type=int)

    def handle(self, *args, **options):
        daily_leave_deduction(options['year'], options['month'], options['day'])

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

def getTime(t):
    return [t[:2],t[2:]]

# categorise_employee function start
# This function will return separate user_id list of ansr_employee, ansr_contract, vendor_employee
def categorise_users():
    users_all = User.objects.filter(is_active=True)
    ansr_employee = []
    ansr_contract = []
    vendor_employee = []
    for user_list in users_all:
        employee = Employee.objects.filter(user_id = user_list.id)
        if employee.count()<1:
            emp_assigned_id = ''
        else:
            emp_assigned_id = employee[0].employee_assigned_id
        # print user_list.id, emp_assigned_id
        if emp_assigned_id == "":
            vendor_employee.append(user_list.id)
        elif emp_assigned_id.isdigit() == False:
            if emp_assigned_id.find("CNT")>-1 or emp_assigned_id.find("CONT")>-1:
                ansr_contract.append(user_list.id)
            else:
                vendor_employee.append(user_list.id)
        else:
            ansr_employee.append(user_list.id)
    return ansr_employee, ansr_contract, vendor_employee
# categorise_employee function end

def daily_leave_deduction(year, month, day):
    print str(datetime.now()) + " daily leave auto apply started running"
    tzone = pytz.timezone('Asia/Kolkata')
    date = datetime(year, month, day)
    start_date = date.date()
    end_date = start_date + timedelta(days=4)
    dates = dates_to_check_leave(start_date, end_date)
    user_id_to_exclude = categorise_users()[2]
    user_list = User.objects.filter(is_active=True, date_joined__lte=dates[4]).exclude(id__in=user_id_to_exclude)
    FMT = '%H:%M:%S'
    holiday = Holiday.objects.all().values('date')
    # dueDate = end_date + timedelta(days=7)
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
                    if employee:
                        manager = user.employee.manager
                    else:
                        manager = ''
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

                                        leaves.append(leave_for_date)
                            elif appliedLeaveCheck[0].days_count == '0.5':
                                reason = "you had applied for only half day leave"
                                leave = 'half_day'
                                if leave:
                                    leave_for_date['date'] = date
                                    leave_for_date['leave'] = leave
                                    leave_for_date['reason'] = reason

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

                                    leaves.append(leave_for_date)
                            elif tdelta < fullDayOfficeStayTimeLimit:
                                reason = "You had logged {0} hr that is below 6 hr".format(stayInTime)
                                leave = 'half_day'
                                if leave:
                                    leave_for_date['date'] = date
                                    leave_for_date['leave'] = leave
                                    leave_for_date['reason'] = reason

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
                                    leaves.append(leave_for_date)
                    else:
                        print(user.first_name + user.last_name + " hr need to take care")
                except:
                    logger.debug("missing records")
        if leaves:
            try:
                applyLeave(user, manager, leaves, year)
            except:
                logger.debug('email send issue user id' + user.id)
    writeFile.close()
    writeFileemail.close()
    new_filename = "DailyLeaveDeduction_" + str(year) + "_" + str(month) + "_" + str(day) + ".csv"
    os.rename(fileName, new_filename)
    print "File " + fileName + " renamed to " + new_filename
    print "Sending deduction report... "
    email_report_send = EmailMessage(
        'Leave Deduction File: ' + str(year) + "_" + str(month) + "_" + str(day),
        'Hi, All, \nPlease find attached leave deduction file.\nThanks!\nMyAnsrSource\n\n',
        settings.EMAIL_HOST_USER,
        ['ravindra.jawari@ansrsource.com'],
        cc=['janaki.BS@ansrsource.com', 'ramesh.kumar@ansrsource.com', 'shalini.bhagat@ansrsource.com']
    )
    email_report_send.attach_file(new_filename)
    email_report_send.send()
    print str(datetime.now()) + " Daily leave check raised finished running"
        # applyLeave(attendance, attendance.for_date.year)
        # print "leave saved for {0}".format(attendance.user)

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

def applyLeave(user, manager, leaves, year):
    for leave in leaves:
        user_id = user.id
        reason = "applied by system"
        applied_by = User.objects.get(id=35).id
        avaliable_leave = avaliableLeaveCheck(user_id, leave, year)
        # import ipdb;
        # ipdb.set_trace()
        if avaliable_leave != 0:
            try:
                if len(avaliable_leave) >= 2:
                    for leave_ty in avaliable_leave:
                        leave_type = LeaveSummary.objects.get(user=user_id, leave_type=leave_ty, year=year)
                        if leavecheckonautoapplydate(leave, user_id):
                            leave['leave'] = 'half_day'
                            leavesubmit(leave, manager, leave_type, user_id, applied_by)
                if len(avaliable_leave) == 1:
                    avaliable_leave.append(0)
                    for leave_ty in avaliable_leave:
                        if leave_ty != 0:
                            leave_type = LeaveSummary.objects.get(user=user_id, leave_type=leave_ty, year=year)
                            if leavecheckonautoapplydate(leave, user_id):
                                leave['leave'] = 'half_day'
                                leavesubmit(leave, manager, leave_type, user_id, applied_by)
                        else:
                            leave_type, created = LeaveSummary.objects.get_or_create(user=User.objects.get(id=user_id),
                                                                                     leave_type=LeaveType.objects.get(
                                                                                         leave_type='loss_of_pay'),
                                                                                     applied=0, approved=0,
                                                                                     balance=0,
                                                                                     year=year)
                            if leavecheckonautoapplydate(leave, user_id):
                                leave['leave'] = 'half_day'
                                leavesubmit(leave, manager, leave_type, user_id, applied_by)

            except:
                leave_type = LeaveSummary.objects.get(user=user_id,leave_type=avaliable_leave,year=year)
                if leavecheckonautoapplydate(leave, user_id):
                    leavesubmit(leave, manager, leave_type, user_id, applied_by)
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
                leavesubmit(leave, manager, leave_type, user_id, applied_by)

def leavecheckonautoapplydate(leave, user):
    leave_check = LeaveApplications.objects.filter(from_date__lte=leave['date'],
                                             to_date__gte=leave['date'],
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


def leavesubmit(leave, user_manager, leave_type,  user_id, applied_by):
    try:
        leaveapp = LeaveApplications.objects.filter(from_date__lte=leave['date'],
                                                 to_date__gte=leave['date'],
                                                 user=user_id,
                                                    status__in=['open', 'approved'])
        if leaveapp and leave['leave'] == 'full_day' and leaveapp[0].leave_type_id not in [16, 11]:
            if leaveapp[0].from_session == 'session_first':
                leavecount = .5
                fromsession = 'session_second'
                tosession = 'session_second'
            else:
                leavecount = .5
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
        manager_employee_id = Employee.objects.get(user_id=manager[0]['user_id'])
        user_employee_id = Employee.objects.get(user_id=user_id)
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
                          daily_deduction=1,
                          ).save()
        leave_type.save()
        try:
            send_mail(User.objects.get(id=user_id),
                      leave_type.leave_type.leave_type,user_manager,
                      leave['date'],
                      leave['date'],
                      leavecount)
        except:
            print "HR need take care for {0}".format(User.objects.get(id=user_id))
        writeFile.write(
            "'{0}','{1}','{2}','{3}','{4}','{5}','{6}'".format(str(User.objects.get(id=user_id)),
                                                               str(user_employee_id.employee_assigned_id),
                                                               str(manager_d),
                                                               str(manager_employee_id.employee_assigned_id),
                                                               str(leave['leave']), str(leave['reason']),
                                                               str(leave['date'])))
        writeFile.write("\n")
        writeFileemail.write(
            "'{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}', '{10}'".format(
                str(User.objects.get(id=user_id).first_name),
                str(user_employee_id.employee_assigned_id),
                str(manager_d),
                str(manager_employee_id.employee_assigned_id),
                str(leave['leave']),
                str(leave['reason']),
                str(leave['date']),
                str(leaveTypeDictionary[leave_type.leave_type.leave_type]),
                str(User.objects.get(id=user_id).email),
                str(user_manager.user.email),"Daily"))
        writeFileemail.write("\n")

    except:
        print "please check manager for user id {0}".format(user_id)
        # logger.error("error happen for {0} while putting forced leave manager is not there".format(user_id))

def send_mail(user, leavetype, user_manager, fromdate, todate, count):
    msg_html = render_to_string('email_templates/short_leave_auto_apply.html',
                                {'registered_by': user.first_name,
                                 'leaveType': leaveTypeDictionary[leavetype],
                                 'fromdate': fromdate,
                                 'todate': todate,
                                 'count': count,
                                 })

    mail_obj = EmailMessage('Leave Deduction',
                            msg_html, settings.EMAIL_HOST_USER, [user.email],
                            cc=[user_manager.user.email])

    mail_obj.content_subtype = 'html'
    email_status = 1
    # email_status = mail_obj.send()
    if email_status == 0:
        logger.error(
            "Unable To send Mail To The Authorities For"
            "The Following Leave Applicant : Date time : ")
        return "failed"
    else:
        logger.debug('send successful')
