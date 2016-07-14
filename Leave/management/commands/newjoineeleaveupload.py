import logging
from django.utils.timezone import get_default_timezone
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.conf import settings
from employee.models import Employee
from Leave.models import LeaveType, LeaveSummary
from django.contrib.auth.models import User
from datetime import date, timedelta

logger = logging.getLogger('MyANSRSource')

class Command(BaseCommand):
    help = 'Upload Leave summary for new joinee.'

    def handle(self, *args, **options):
        newJoineeCron()

def newJoineeCron():
    newUsers = Employee.objects.filter()
    leaveTypeList = LeaveType.objects.all()
    for user in newUsers:
        user_temp = User.objects.get(id = user.user_id)
        if user_temp.is_active == True:

            leavesummry = LeaveSummary.objects.filter(user = user_temp)
            avaliableLeave = []
            if leavesummry:
                avaliableLeave = [x.leave_type for x in leavesummry ]
            for leave_type_obj in leaveTypeList:
                if leave_type_obj not in avaliableLeave:
                    if leave_type_obj.occurrence == 'yearly':
                        if user.gender=='F' and leave_type_obj.leave_type=='maternity_leave':
                            LeaveSummary.objects.create(user=user_temp, leave_type=leave_type_obj,
                                                                      year=date.today().year,
                                                                      applied =0,
                                                                      approved = 0,
                                                                      balance = leave_type_obj.count)
                        elif user.gender=='M' and leave_type_obj.leave_type=='paternity_leave':
                            LeaveSummary.objects.create(user=user_temp, leave_type=leave_type_obj,
                                                                      year=date.today().year,
                                                                      applied =0,
                                                                      approved = 0,
                                                                      balance = leave_type_obj.count)
                        elif leave_type_obj.leave_type=='bereavement_leave':
                            LeaveSummary.objects.create(user=user_temp, leave_type=leave_type_obj,
                                                                      year=date.today().year,
                                                                      applied =0,
                                                                      approved = 0,
                                                                      balance = leave_type_obj.count)

                    else:
                        LeaveSummary.objects.create(user=user_temp, leave_type=leave_type_obj,
                                                                  year=date.today().year,
                                                                  applied =0,
                                                                  approved = 0,
                                                                  balance = 0)