from Leave.models import ShortAttendance, LeaveApplications, LeaveSummary, LeaveType
from employee.models import Employee
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.core.management.base import BaseCommand
import logging


logger = logging.getLogger('MyANSRSource')


class Command(BaseCommand):
    help = 'Upload Leave summary for new joinee.'

    def handle(self, *args, **options):
        shortAttendanceApply()


def shortAttendanceApply():
    duedate = date.today() + timedelta(days=1)
    shortattendance = ShortAttendance.objects.filter(due_date=duedate,active=True)
    for attendance in shortattendance:
        applyLeave(attendance)
        print "leave saved for {0}".format(attendance.user)


def applyLeave(attendance):

    user_id = attendance.user.id
    reason = "applied by system because dispute not resolved"
    applied_by = User.objects.get(id=35).id

    avaliable_leave = avaliableLeaveCheck(user_id, attendance.short_leave_type)
    if avaliable_leave!=0:
        leave = LeaveSummary.objects.get(user=user_id,
                                         leave_type=avaliable_leave,
                                         year=date.today().year)
        leavesubmit(attendance, leave, reason, user_id, applied_by)
    else:
        leave = LeaveSummary.objects.filter(user=user_id,
                                         leave_type__leave_type='loss_of_pay',
                                         year=date.today().year)
        if leave:
            leave = leave[0]
        else:
            leave, created = LeaveSummary.objects.get_or_create(user=User.objects.get(id=user_id),
                                        leave_type=LeaveType.objects.get(leave_type='loss_of_pay'),
                                        applied=0, approved=0,
                                        balance=0,
                                        year=date.today().year)
        leavesubmit(attendance, leave, reason, user_id, applied_by)


def avaliableLeaveCheck(user_id, short_leave_type):
    leavesavaliableforapply = ['casual_leave','earned_leave']
    for val in leavesavaliableforapply:
        leave = LeaveSummary.objects.filter(user=user_id, leave_type__leave_type=val, year=date.today().year)
        if short_leave_type == 'full_day' and leave and float(leave[0].balance.encode('utf-8')) >= 1:
            return leave[0].leave_type
        elif leave and leave and float(leave[0].balance.encode('utf-8'))>0:
            return leave[0].leave_type
    return 0


def leavesubmit(attendance, leave, reason, user_id, applied_by):
    try:
        if attendance.short_leave_type == 'full_day':
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

    except:
        print "please check manager for user id {0}".format(user_id)
        # logger.error("error happen for {0} while putting forced leave manager is not there".format(user_id))
