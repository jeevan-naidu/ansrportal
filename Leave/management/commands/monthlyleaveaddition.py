from django.contrib.auth.models import User
from Leave.models import *
from employee.models import Employee
from datetime import date, timedelta
from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger('MyANSRSource')


class Command(BaseCommand):
    help = 'Upload Leave summary for new joinee.'

    def handle(self, *args, **options):
        monthlyLeaveAdditionCron()

def monthlyLeaveAdditionCron():
    users = User.objects.filter(is_active = True)
    todaydate = date.today()
    todaydateDay = todaydate.day
    todaydateMonth = todaydate.month
    todaydateYear = todaydate.year
    for user in users:
        leaves = LeaveSummary.objects.filter(user = user, leave_type__occurrence = 'monthly')
        joiningdate = user.date_joined.date()
        joiningdateDay = joiningdate.day
        joiningdateMonth = joiningdate.month
        joiningdateYear = joiningdate.year
        for leave in leaves:
            if todaydateYear == joiningdateYear and todaydateMonth==joiningdateMonth:
                if leave.leave_type.carry_forward == 'yearly':
                    if joiningdateDay>0 and joiningdateDay<11:
                        leave.balance = leave.balance + .5
                    elif joiningdateDay>10 and joiningdateDay<21:
                        leave.balance = leave.balance + 1
                    else:
                        leave.balance = leave.balance + 1.5
                elif leave.leave_type.carry_forward == 'monthly':
                    if joiningdateDay>25:
                        leaveTotal = leaveTotal + .5
            else:
                leave.balance = float(leave.balance) + float((leave.leave_type.count).encode('utf-8'))
            leave.save()