from django.contrib.auth.models import User
from Leave.models import *
from datetime import date
from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger('MyANSRSource')


class Command(BaseCommand):
    help = 'Upload Leave summary for new joinee.'

    def handle(self, *args, **options):
        monthlyLeaveAdditionCron()

def monthlyLeaveAdditionCron():
    users = User.objects.filter(is_active = True)
    current_year = date.today().year
    current_month = date.today().month
    admin = User.objects.get(id=35)
    for user in users:
        try:
            leaves = LeaveSummary.objects.filter(user = user, leave_type__occurrence = 'monthly',year=current_year)
            for leave in leaves:
                if leave.leave_type.carry_forward != 'none':
                    CreditEntry.objects.create(user=user,
                                               year=current_year,
                                               month=current_month,
                                               leave_type=leave.leave_type,
                                               days=leave.leave_type.count,
                                               status_action_by=admin,
                                               comments="monthly leave credit")
                    leave.balance = float(leave.balance) + float((leave.leave_type.count).encode('utf-8'))
                    leave.save()
                    print "leave added for {0} {1} leave type id {2} balance is {3}".format(user.first_name,
                                                                                            user.last_name,
                                                                                            leave.leave_type_id,
                                                                                            leave.balance)
                else:
                    CreditEntry.objects.create(user=user,
                                               year=current_year,
                                               month=current_month,
                                               leave_type=leave.leave_type,
                                               days=leave.leave_type.count,
                                               status_action_by=admin,
                                               comments="monthly leave credit")
                    leave.balance = float((leave.leave_type.count).encode('utf-8'))
                    leave.save()
                    print "leave added for {0} {1} leave type id {2} balance is {3}".format(user.first_name,
                                                                                            user.last_name,
                                                                                            leave.leave_type_id,
                                                                                            leave.balance)


        except:
            logger.error("error happens for {0}".format(user.id))
