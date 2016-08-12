from Leave.models import ShortAttendance, LeaveApplications, LeaveSummary
from django.contrib.auth.models import User
from datetime import date,datetime, timedelta, time
from django.core.management.base import BaseCommand
import logging


logger = logging.getLogger('MyANSRSource')


class Command(BaseCommand):
    help = 'Upload Leave summary for new joinee.'

    def handle(self, *args, **options):
        shortAttendanceApply()


def shortAttendanceApply():
    import ipdb
    ipdb.set_trace()
    duedate = '2016-08-21'
    shortattendance = ShortAttendance.objects.filter(due_date=duedate,active=True)
    for attendance in shortattendance:
        applyLeave(attendance)
        print "leave saved for {0}".format(attendance.user)


def applyLeave(attendance):
    # import ipdb
    # ipdb.set_trace()
    user_id = attendance.user.id
    reason = "applied by system because dispute not resolved"
    applied_by = User.objects.get(id=35).id

    avaliable_leave = avaliableLeaveCheck(user_id, attendance.short_leave_type)
    if avaliable_leave!=0:
        leave = LeaveSummary.objects.get(user=user_id, leave_type=avaliable_leave, year=date.today().year)
        leavesubmit(attendance, leave, reason, user_id, applied_by)
    else:
        leave = LeaveSummary.objects.get(user=user_id, leave_type__leave_type='loss_of_pay', year=date.today().year)
        LeaveSummary.objects.create(user=user_id, leave_type__leave_type='loss_of_pay', applied=0, approved=0, balance=0,
                                        year=date.today().year)
        leavesubmit(attendance, leave, reason, user_id, applied_by)




def avaliableLeaveCheck(user_id, short_leave_type):
    # import ipdb
    # ipdb.set_trace()
    leavesavaliableforapply = ['casula_leave','earned_leave']
    for val in leavesavaliableforapply:
        leave = LeaveSummary.objects.filter(user=user_id, leave_type__leave_type=val, year=date.today().year)
        if short_leave_type == 'full_day' and leave and leave[0].balance>=1:
            return val
        elif leave and leave[0].balance>0:
            return val

    return 0

def leavesubmit(attendance,leave,reason,user_id,applied_by):
    # import ipdb
    # ipdb.set_trace()
    if attendance.short_leave_type == 'full_day':
        leavecount = 1
        fromsession = 'first_session'
        tosession = 'second_session'
    else:
        leavecount = .5
        fromsession = 'first_session'
        tosession = 'first_session'
    leave.balance = float(leave.balance) - leavecount
    leave.approved = float(leave.approved) + leavecount
    LeaveApplications(leave_type=leave.leave_type, from_date=attendance.due_date, to_date=attendance.due_date,
                      from_session=fromsession,
                      to_session=tosession,
                      days_count=1, reason=reason,
                      status='approved').saveas(user_id, applied_by)
    attendance.active = False
    attendance.save()
    leave.save()
