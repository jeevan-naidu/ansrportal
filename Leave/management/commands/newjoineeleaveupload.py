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
    '''
    who ever is not having entry in leave summry table but in emoployee table
    Returns
    -------
    create entry
    '''
    newUsers = Employee.objects.filter()
    leaveTypeList = LeaveType.objects.all()
    for user in newUsers:
        try:
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
                                print "entry got created for {0} {1} leavetype {2}".format(user_temp.first_name,
                                                                                           user_temp.last_name,
                                                                                           leave_type_obj)
                            elif user.gender=='M' and leave_type_obj.leave_type=='paternity_leave':
                                LeaveSummary.objects.create(user=user_temp, leave_type=leave_type_obj,
                                                                          year=date.today().year,
                                                                          applied =0,
                                                                          approved = 0,
                                                                          balance = leave_type_obj.count)
                                print "entry got created for {0} {1} leavetype {2}".format(user_temp.first_name,
                                                                                           user_temp.last_name,
                                                                                           leave_type_obj)
                            elif leave_type_obj.leave_type=='bereavement_leave':
                                LeaveSummary.objects.create(user=user_temp, leave_type=leave_type_obj,
                                                                          year=date.today().year,
                                                                          applied =0,
                                                                          approved = 0,
                                                                          balance = leave_type_obj.count)
                                print "entry got created for {0} {1} leavetype {2}".format(user_temp.first_name,
                                                                                           user_temp.last_name,
                                                                                           leave_type_obj)
                            elif leave_type_obj.leave_type=='sabbatical':
                                LeaveSummary.objects.create(user=user_temp, leave_type=leave_type_obj,
                                                                          year=date.today().year,
                                                                          applied =0,
                                                                          approved = 0,
                                                                          balance = leave_type_obj.count)
                                print "entry got created for {0} {1} leavetype {2}".format(user_temp.first_name,
                                                                                           user_temp.last_name,
                                                                                           leave_type_obj)
                        elif leave_type_obj.occurrence == 'monthly':
                            leavetotal = monthlyLeaveAdd(user, leave_type_obj)
                            #leavetotal = 0
                            LeaveSummary.objects.create(user=user_temp, leave_type=leave_type_obj,
                                                        year=date.today().year,
                                                        applied=0,
                                                        approved=0,
                                                        balance=leavetotal)
                            print "entry got created for {0} {1} leavetype {2}".format(user_temp.first_name,
                                                                                       user_temp.last_name,
                                                                                       leave_type_obj)

                        else:
                            LeaveSummary.objects.create(user=user_temp, leave_type=leave_type_obj,
                                                                      year=date.today().year,
                                                                      applied =0,
                                                                      approved = 0,
                                                                      balance = 0)
                            print "entry got created for {0} {1} leavetype {2}".format(user_temp.first_name,
                                                                                       user_temp.last_name,
                                                                                       leave_type_obj)

        except:
            logger.error("error happen for {0} {1} while creating entry in leavesummry table".format(user_temp.first_name,user_temp.last_name))


def monthlyLeaveAdd(user, leave):
    '''
    Leave addition for earned leave
    casual leave, sick leave based on joining date.
    New entry in employee table
    '''
    try:
        todaydate = date.today()
        todaydateMonth = todaydate.month
        todaydateYear = todaydate.year
        joiningdate = user.joined
        joiningdateDay = joiningdate.day
        joiningdateMonth = joiningdate.month
        joiningdateYear = joiningdate.year
        leavetotal=0
        if todaydateYear == joiningdateYear: #and todaydateMonth==joiningdateMonth:
            if leave.carry_forward == 'yearly':
                if joiningdateDay > 0 and joiningdateDay < 11:
                    leavetotal = 1.5
                elif joiningdateDay > 10 and joiningdateDay < 21:
                    leavetotal = 1
                else:
                    leavetotal = .5
                leavetotal = leavetotal + float((leave.count).encode('utf-8')) * (todaydateMonth - joiningdateMonth)

            elif leave.carry_forward == 'monthly':
                if joiningdateDay < 6:
                    leavetotal = .5
                leavetotal = leavetotal + float((leave.count).encode('utf-8')) * (todaydateMonth - joiningdateMonth)
            else:
                leavetotal = 2

        return leavetotal


    except:
        logger.error("user having issue{}")

