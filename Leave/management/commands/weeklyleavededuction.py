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

# def previous_week_range(date):
#     week_dates = []
#     for week_no in [2]:
#         start_date = date + timedelta(-date.weekday(), weeks=-week_no)
#         end_date = date + timedelta(-date.weekday() - 1)
#         week_dates.append(start_date)
#         week_dates.append(end_date)
#     return week_dates

def previous_week_range(date):
    start_date = date + timedelta(-date.weekday(), weeks=-2)
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

    def handle(self, *args, **options):
        weekly_leave_deduction()

def weekly_leave_deduction():
    tzone = pytz.timezone('Asia/Kolkata')
    user_list = User.objects.filter(is_active=True)
    date = datetime.now().date()
    year = date.year
    week_dates = previous_week_range(date)
    start_date = week_dates[0]
    end_date = week_dates[1]
    dates = dates_to_check_leave(start_date, end_date)
    holiday = Holiday.objects.all().values('date')
    # print str(date) + " short attendance raised started running"
    FMT = '%H:%M:%S'
    dueDate = end_date + timedelta(days=7)
    fullDayOfficeStayTimeLimit = timedelta(hours=6, minutes=00, seconds=00)
    halfDayOfficeStayTimeLimit = timedelta(hours=3, minutes=00, seconds=00)
    for user in user_list:
        leaves = []
        leave_for_date = {}
        employee_attendance = []
        for date in dates:
            if date in [datedata['date'] for datedata in holiday]:
                employee_attendance.append(9)
                break
            if date.weekday() >= 5:
                break
            try:
                employee = Employee.objects.filter(user_id=user.id)
                appliedLeaveCheck = LeaveApplications.objects.filter(from_date__lte=date,
                                                                     to_date__gte=date,
                                                                     user=user.id,
                                                                     status__in=['open', 'approved'])
                if employee:
                    attendance = Attendance.objects.filter(attdate=date, incoming_employee_id=employee[0].employee_assigned_id)
                    if appliedLeaveCheck:
                        if appliedLeaveCheck[0].leave_type_id == 16:
                            temp_id = appliedLeaveCheck.temp_id
                            attendance = Attendance.objects.filter(attdate=date,
                                                                   incoming_employee_id=temp_id)
                            if attendance:
                                swipeIn = attendance[0].swipe_in.astimezone(tzone)
                                swipeOut = attendance[0].swipe_out.astimezone(tzone)
                                swipeInTime = swipeIn.strftime("%H:%M:%S")
                                swipeOutTime = swipeOut.strftime("%H:%M:%S")
                                tdelta = datetime.strptime(swipeOutTime, FMT) - datetime.strptime(swipeInTime, FMT)
                                stayInTime = getTimeFromTdelta(tdelta, "{H:02}:{M:02}:{S:02}")
                                employee_attendance.append(tdelta)
                        elif appliedLeaveCheck[0].leave_type_id == 11:
                                tdelta = appliedLeaveCheck[0].hours
                                employee_attendance.append(tdelta)
                    if attendance:
                        for att in attendance:
                            if att.swipe_out and att.swipe_in is not None:
                                att_day = att.swipe_out - att.swipe_in
                                delta = att_day
                                sec = delta.seconds
                                hours = sec // 3600
                                minutes = (sec // 60) - (hours * 60)
                                att_day = ('{0}.{1}'.format(hours, minutes))
                                att_day = float(att_day)
                                employee_attendance.append(round(att_day, 2))
                    else:
                        employee_attendance.append(0)
                        leave_for_date['reason'] = 'you were absent'
                        leave_for_date['user_id'] = user.id
                        leave_for_date['leave'] = 'full_day'
                        leave_for_date['date'] = date
                        leaves.append(leave_for_date)
                    if len(appliedLeaveCheck)>1:
                        pass
                    elif len(appliedLeaveCheck)==1 and appliedLeaveCheck[0].from_date==date and appliedLeaveCheck[0].to_date==date and appliedLeaveCheck[0].from_session=='session_first' and appliedLeaveCheck[0].to_session== 'session_second':
                        employee_attendance.append(9)
                        pass
                    elif len(appliedLeaveCheck)==1 and appliedLeaveCheck[0].from_date<date and appliedLeaveCheck[0].to_date>date:
                        pass
                    elif len(appliedLeaveCheck)==1 and appliedLeaveCheck[0].from_date==date and appliedLeaveCheck[0].to_date>date and appliedLeaveCheck[0].from_session=='session_first':
                        pass
                    elif len(appliedLeaveCheck) == 1 and appliedLeaveCheck[0].from_date < date and appliedLeaveCheck[
                        0].to_date == date and appliedLeaveCheck[0].to_session== 'session_second':
                        pass
                    elif len(appliedLeaveCheck) == 1 and appliedLeaveCheck[0].from_date == date and appliedLeaveCheck[
                        0].to_date == date and appliedLeaveCheck[0].to_session== 'session_second' and appliedLeaveCheck[0].from_session== 'session_second':
                        employee_attendance.append(4.5)
                        pass
                    elif len(appliedLeaveCheck) == 1 and appliedLeaveCheck[0].from_date == date and appliedLeaveCheck[
                        0].to_date == date and appliedLeaveCheck[0].to_session== 'session_first' and appliedLeaveCheck[0].from_session== 'session_first':
                        employee_attendance.append(4.5)
                        pass
                else:
                    print(user.first_name + user.last_name + " hr need to take care")
            except:
                print("missing records")
        if employee_attendance:
            try:
                if 39.5 < sum(employee_attendance) < 44:
                    leave_for_date['reason'] = "you had put " + str(sum(employee_attendance)) + " hours which is below 44 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'half_day'
                    leave_for_date['date'] = dates[0]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 35 < sum(employee_attendance) < 39.5:
                    leave_for_date['reason'] = "you had put " + str(sum(employee_attendance)) + " hours which is below 39.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[0]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 30.5 < sum(employee_attendance) < 35:
                    leave_for_date['reason'] = "you had put " + str(sum(employee_attendance)) + " hours which is below 35 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'half_day'
                    leave_for_date['date'] = dates[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 35 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[1]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 26 < sum(employee_attendance) < 30.5:
                    leave_for_date['reason'] = "you had put " + str(sum(employee_attendance)) + " hours which is below 30.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 30.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[1]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 21.5 < sum(employee_attendance) < 26:
                    leave_for_date['reason'] = "you had put " + str(sum(employee_attendance)) + " hours which is below 26 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(sum(employee_attendance)) + " hours which is below 26 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[1]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 26 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'half_day'
                    leave_for_date['date'] = dates[2]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 17 < sum(employee_attendance) < 21.5:
                    leave_for_date['reason'] = "you had put " + str(sum(employee_attendance)) + " hours which is below 21.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 21.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[1]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 21.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[2]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 12.5 < sum(employee_attendance) < 17:
                    leave_for_date['reason'] = "you had put " + str(sum(employee_attendance)) + " hours which is below 17.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 17.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[1]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 17.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[2]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 17.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'half_day'
                    leave_for_date['date'] = dates[3]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 9 < sum(employee_attendance) < 12.5:
                    leave_for_date['reason'] = "you had put " + str(sum(employee_attendance)) + " hours which is below 12.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 12.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[1]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 12.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[2]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 12.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[3]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 4.5 < sum(employee_attendance) < 9:
                    leave_for_date['reason'] = "you had put " + str(sum(employee_attendance)) + " hours which is below 9 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 9 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[1]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 9 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[2]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 9 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[3]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 9 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'half_day'
                    leave_for_date['date'] = dates[4]
                    leaves.append(leave_for_date)
                    applyLeave(user, leaves, year)
                elif 0 < sum(employee_attendance) < 4.5:
                    leave_for_date['reason'] = "you had put " + str(sum(employee_attendance)) + " hours which is below 4.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[0]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 4.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[1]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 4.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[2]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 4.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[3]
                    leaves.append(leave_for_date)
                    leave_for_date = {}
                    leave_for_date['reason'] = "you had put " + str(
                        sum(employee_attendance)) + " hours which is below 4.5 hours"
                    leave_for_date['user_id'] = user.id
                    leave_for_date['leave'] = 'full_day'
                    leave_for_date['date'] = dates[4]
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
        avaliable_leave = avaliableLeaveCheck(user_id, leave['leave'], year)
        if avaliable_leave != 0:
            leave_type = LeaveSummary.objects.get(user=user_id,leave_type=avaliable_leave,year=year)
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
    leave_check = LeaveApplications.objects.filter(from_date__lte=leave['date'],
                                             to_date__gte=leave['date'],
                                             user=user)
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
    for val in leavesavaliableforapply:
        leave = LeaveSummary.objects.filter(user=user_id, leave_type__leave_type=val, year=year)
        if short_leave_type == 'full_day' and leave and float(leave[0].balance.encode('utf-8')) >= 1:
            return leave[0].leave_type
        elif leave and leave and float(leave[0].balance.encode('utf-8'))>0:
            return leave[0].leave_type
    return 0

def leavesubmit(leave, leave_type,  user_id, applied_by):
    try:
        leaveapp = LeaveApplications.objects.filter(from_date__lte=leave['date'],
                                                 to_date__gte=leave['date'],
                                                 user=user_id,
                                                    status__in=['open', 'approved'])
        if leaveapp and leave['leave'] == 'full_day':
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