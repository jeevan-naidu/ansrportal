from Leave.models import ShortAttendance, LeaveApplications, LeaveSummary, LeaveType
from employee.models import Employee
from django.contrib.auth.models import User
from datetime import date, timedelta, datetime
from django.core.management.base import BaseCommand
import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from Leave.tasks import leaveTypeDictionary

logger = logging.getLogger('MyANSRSource')


class Command(BaseCommand):
    help = 'Upload Leave summary for new joinee.'

    def handle(self, *args, **options):
        shortAttendanceApply()


def shortAttendanceApply():
    print str(datetime.now()) + " short attendance auto apply started running"
    duedate = date.today() - timedelta(days=1)
    shortattendance = ShortAttendance.objects.filter(due_date=duedate, active=True)
    for attendance in shortattendance:
        applyLeave(attendance, attendance.for_date.year)
        print "leave saved for {0}".format(attendance.user)
    print str(datetime.now()) + " short attendance auto apply finished running. processed data "\
                                + str(len(shortattendance))


def applyLeave(attendance, year):

    user_id = attendance.user.id
    reason = "applied by system"
    applied_by = User.objects.get(id=35).id

    avaliable_leave = avaliableLeaveCheck(user_id, attendance.short_leave_type, year)
    if avaliable_leave!=0:
        leave = LeaveSummary.objects.get(user=user_id,
                                         leave_type=avaliable_leave,
                                         year=year)
    else:
        leave = LeaveSummary.objects.filter(user=user_id,
                                         leave_type__leave_type='loss_of_pay',
                                         year=year)
        if leave:
            leave = leave[0]
        else:
            leave, created = LeaveSummary.objects.get_or_create(user=User.objects.get(id=user_id),
                                        leave_type=LeaveType.objects.get(leave_type='loss_of_pay'),
                                        applied=0, approved=0,
                                        balance=0,
                                        year=year)
    if leavecheckonautoapplydate(attendance, user_id):
        leavesubmit(attendance, leave, reason, user_id, applied_by)
    else:
        attendance.active = False
        attendance.save()


def avaliableLeaveCheck(user_id, short_leave_type, year):
    leavesavaliableforapply = ['casual_leave', 'earned_leave']
    for val in leavesavaliableforapply:
        leave = LeaveSummary.objects.filter(user=user_id, leave_type__leave_type=val, year=year)
        if short_leave_type == 'full_day' and leave and float(leave[0].balance.encode('utf-8')) >= 1:
            return leave[0].leave_type
        elif leave and leave and float(leave[0].balance.encode('utf-8'))>0:
            return leave[0].leave_type
    return 0


def leavesubmit(attendance, leave, reason, user_id, applied_by):
    try:
        leaveapp = LeaveApplications.objects.filter(from_date__lte=attendance.for_date,
                                                 to_date__gte=attendance.for_date,
                                                 user=user_id,
                                                    status__in=['open', 'approved'])
        if leaveapp and attendance.short_leave_type == 'full_day':
            leavecount = .5
            if leaveapp[0].from_session == 'session_first':
                fromsession = 'session_second'
                tosession = 'session_second'
            else:
                fromsession = 'session_first'
                tosession = 'session_first'
        elif attendance.short_leave_type == 'full_day':
            leavecount = 1
            fromsession = 'session_first'
            tosession = 'session_second'
        else:
            leavecount = .5
            fromsession = 'session_first'
            tosession = 'session_first'
        leave.balance = float(leave.balance) - leavecount
        leave.approved = float(leave.approved) + leavecount
        manager_id = Employee.objects.filter(user_id=user_id).values('manager_id')
        manager = Employee.objects.filter(employee_assigned_id=manager_id).values('user_id')
        manager_d = User.objects.get(id=manager[0]['user_id'])
        applied_by = User.objects.get(id=applied_by)
        LeaveApplications(user=User.objects.get(id=user_id),
                          leave_type=leave.leave_type,
                          from_date=attendance.for_date,
                          to_date=attendance.for_date,
                          from_session=fromsession,
                          to_session=tosession,
                          days_count=leavecount, reason=reason,
                          status='approved',
                          status_action_by=applied_by,
                          applied_by=applied_by,
                          apply_to=manager_d,
                          ).save()
        attendance.active = False
        attendance.save()
        leave.save()
        send_mail(User.objects.get(id=user_id),
                  leave.leave_type.leave_type,
                  attendance.for_date,
                  attendance.for_date,
                  leavecount)

    except:
        print "please check manager for user id {0}".format(user_id)
        # logger.error("error happen for {0} while putting forced leave manager is not there".format(user_id))


def leavecheckonautoapplydate(attendance, user):
    leave = LeaveApplications.objects.filter(from_date__lte=attendance.for_date,
                                             to_date__gte=attendance.for_date,
                                             user=user)
    if leave and \
                    len(leave) > 1 or\
                    attendance.short_leave_type == 'half_day' and leave or leave and\
                            leave[0].from_session == 'session_first'\
            and leave[0].to_session == 'session_second':
        return False
    else:
        return True


def send_mail(user, leavetype, fromdate, todate, count):
    msg_html = render_to_string('email_templates/short_leave_auto_apply.html',
                                {'registered_by': user.first_name,
                                 'leaveType': leaveTypeDictionary[leavetype],
                                 'fromdate': fromdate,
                                 'todate': todate,
                                 'count': count,
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