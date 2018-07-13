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

def monthlyLeaveAdditionCron():

    ansr_contract = categorise_users()[1]
    vendor_employee = categorise_users()[2]
    user_id_to_exclude = ansr_contract + vendor_employee
    users = User.objects.filter(is_active = True).exclude(id__in=user_id_to_exclude)

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

    # 1 casual leave for ansr contract employee
    for user in ansr_contract:
        try:
            leaves = LeaveSummary.objects.filter(user_id = user, leave_type__occurrence = 'monthly',year=current_year, leave_type_id=3)
            for leave in leaves:
                if leave.leave_type.carry_forward != 'none':
                    CreditEntry.objects.create(user_id=user,
                                               year=current_year,
                                               month=current_month,
                                               leave_type=leave.leave_type,
                                               days=1,
                                               status_action_by=admin,
                                               comments="monthly leave credit")
                    leave.balance = float(leave.balance) + float(1)
                    leave.save()
                    print "casual leave added for contract employee user id: {0}".format(user)
                else:
                    CreditEntry.objects.create(user_id=user,
                                               year=current_year,
                                               month=current_month,
                                               leave_type=leave.leave_type,
                                               days=1,
                                               status_action_by=admin,
                                               comments="monthly leave credit")
                    leave.balance = float(1)
                    leave.save()
                    print "casual leave added for contract employee user id: {0}".format(user)


        except:
            logger.error("error happens for contract employee user id: {0}".format(user))
