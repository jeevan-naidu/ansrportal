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
    for user in users:
        leaves = LeaveSummary.objects.filter(user = user, leave_type__occurrence = 'monthly')
        for leave in leaves:
            leave.balance = float(leave.balance) + float((leave.leave_type.count).encode('utf-8'))
            leave.save()
            print "leave added for {0} {1} leave type id {2} balance is {3}".format(user.first_name,
                                                                                         user.last_name,
                                                                                         leave.leave_type_id,
                                                                                         leave.balance)