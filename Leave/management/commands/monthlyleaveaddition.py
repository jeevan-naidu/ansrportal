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
        try:
            leaves = LeaveSummary.objects.filter(user = user, leave_type__occurrence = 'monthly',year=date.today().year)
            for leave in leaves:
                if leave.leave_type.carry_forward != 'none':
                    leave.balance = float(leave.balance) + float((leave.leave_type.count).encode('utf-8'))
                    leave.save()
                    print "leave added for {0} {1} leave type id {2} balance is {3}".format(user.first_name,
                                                                                            user.last_name,
                                                                                            leave.leave_type_id,
                                                                                            leave.balance)
                else:
                    leave.balance = float((leave.leave_type.count).encode('utf-8'))
                    leave.save()
                    print "leave added for {0} {1} leave type id {2} balance is {3}".format(user.first_name,
                                                                                            user.last_name,
                                                                                            leave.leave_type_id,
                                                                                            leave.balance)


        except:
            logger.error("error happens for {0}".format(user.id))