from datetime import date,timedelta
from django.db.models import Q
from employee.models import Employee
from django.contrib.auth.models import User
from CompanyMaster.models import Holiday
from models import LeaveApplications, LeaveType, LeaveSummary

def leaveValidation(leave_form, user, attachment=None):
    ''' leave types which needs from and to dates'''
    result = {'errors' : [], 'success':[]}
    lateLeaveApplication = lateLeaveCheck(leave_form, user)
    if lateLeaveApplication['error']:
        result['errors'].append( lateLeaveApplication['error'])

    fromDate = leave_form.cleaned_data['fromDate']
    toDate = leave_form.cleaned_data['toDate']
    fromSession = leave_form.cleaned_data['from_session']
    tosession = leave_form.cleaned_data['to_session']
    if fromDate <= toDate :
        if fromDate == toDate and fromSession== 'session_second' and tosession== 'session_first':
            result['errors'].append("Please enter the correct session details.")
            return result
        leave_between_applied_date = LeaveApplications.objects.filter(Q(Q(from_date__lte =fromDate) & Q(to_date__gte= fromDate))| Q(Q(from_date__gte=fromDate) & Q(to_date__lte=toDate))| Q(Q(from_date__lte = toDate) & Q(to_date__gte = toDate)), status__in=['approved', 'open'],user=user)
        if len(leave_between_applied_date)>1 or leaveCheckBetweenAppliedLied(leave_between_applied_date, leave_form):
            result['errors'].append('You have already applied for leave in this time period')
        result_temp = validation_leave_type(leave_form, user, fromDate, toDate, attachment)

        if result_temp['success']:
            result['success'] = result_temp['success']

        else:
            result['errors'].append(result_temp['errors'])

    else:
        result['errors'].append("The From date should be before the To date. ")
    return result

def oneTimeLeaveValidation(leave_form, user):
    ''' leave types which needs only from date '''
    holiday = Holiday.objects.all().values('date')
    result = {'errors' : [], 'success':[], 'todate':[0], 'due_date':[0]}
    lateLeaveApplication = lateLeaveCheck(leave_form, user)
    if lateLeaveApplication['error']:
        result['errors'].append( lateLeaveApplication['error'])

    leaveType_selected = leave_form.cleaned_data['leave']
    leaveType=LeaveType.objects.get(leave_type= leaveType_selected)
    fromDate = leave_form.cleaned_data['fromDate']
    joined_date = Employee.objects.filter(user_id=user).values('joined')
    if joined_date[0]['joined'] > fromDate:
        result['errors'].append('You cannot apply for leave for the period before your date of joining')
    if leaveType_selected in ['maternity_leave', 'paternity_leave', 'bereavement_leave']:
        leaveapproved = getLeaveApproved(user, getLast_day_of_month(fromDate), leaveType)
        if leaveapproved == 0 and not newJoineeValidation(user, fromDate):
            result['success'] = getLeaveBalance(leaveType, fromDate, user)
            result['todate'] = date_by_adding_business_days(fromDate, result['success'],holiday, leaveType_selected)
        elif leaveType_selected in ['paternity_leave', 'bereavement_leave'] and leaveapproved == 0:
            result['success'] = getLeaveBalance(leaveType, fromDate, user)
            result['todate'] = date_by_adding_business_days(fromDate, result['success'],holiday, leaveType_selected)
        else:
            result['errors'].append("You do not have the necessary leave balance to avail of this leave.")
    else:
        holiday = Holiday.objects.all().values('date')
        result['success'] = 1
        result['todate'] = fromDate
        result['due_date'] = fromDate - timedelta(days = int(leaveType.apply_within_days))
        check_date = date.today() - timedelta(days = int(leaveType.apply_within_days))
        if check_date > fromDate:
            result['errors'].append('Leave has expired')
        leaveapproved = getLeaveApproved(user, getLast_day_of_month(fromDate), leaveType)
        if leaveType_selected != 'comp_off_avail' and leaveapproved ==1:
            result['errors'].append('sorry you already applied for comp off/pay off')
        elif fromDate.strftime("%A") not in ("Saturday", "Sunday") and leaveType_selected != 'comp_off_avail':
            flag = False
            for dates in holiday:
                if fromDate == dates['date']:
                    flag = True
            if not flag:
                result['errors'].append('You can only earn comp offs and payoffs for working on weekends or holidays. ')
        elif leaveType_selected == 'comp_off_avail' and fromDate.strftime("%A") in ("Saturday", "Sunday") or fromDate in [holiday1['date'] for holiday1 in holiday]:
            result['errors'].append('You have applied for leave on a holiday.')

    if result['todate'] != [0]:
        toDate = result['todate']
    else:
        toDate = fromDate
    leave_between_applied_date = LeaveApplications.objects.filter(Q(Q(from_date__lte =fromDate) & Q(to_date__gte= fromDate))| Q(Q(from_date__gte=fromDate) & Q(to_date__lte=toDate))| Q(Q(from_date__lte = toDate) & Q(to_date__gte = toDate)),
    status__in=['approved', 'open'],user=user)
    if leave_between_applied_date:
        result['errors'].append( "You have already applied for leave in this time period")

    return result




def validation_leave_type(leave_form, user, fromDate, toDate, attachment):
    ''' validations for new joinees based on leave type, holidays, sabbatical'''
    result = {'errors' : [], 'success':[]}
    fromSession = leave_form.cleaned_data['from_session']
    toSession = leave_form.cleaned_data['to_session']
    leaveType_selected = leave_form.cleaned_data['leave']
    leaveType=LeaveType.objects.get(leave_type= leaveType_selected)
    leavecount = leave_calculation(fromDate, toDate, fromSession, toSession, leaveType_selected)
    joined_date = Employee.objects.filter(user_id=user).values('joined')
    if leavecount <=0:
        result['errors'] = 'You have applied for leave on a holiday.'
        return result
    elif joined_date[0]['joined'] > fromDate:
        result['errors'] = 'You cannot apply for leave for the period before your date of joining'
        return result
    approvedLeave_newjoinee = getLeaveApproved(user)
    if leaveType_selected == 'sabbatical' :

        if leavecount  < 180 and leavecount>=30 and joined_date[0]['joined'] < fromDate:
            result['success'] = leavecount
            return result
        elif leavecount<30 :
            result['errors'] = 'You cannot apply for sabbatical leave for fewer than 30 calendar days.'
            return result
        elif leavecount>180 :
            result['errors'] = 'You do not have the necessary leave balance to avail of this leave.'
            return result
        else :
            result['errors'] = 'You are not allowed to take leave for this time period'
            return result

    elif leaveType_selected == 'loss_of_pay' :
        result['success'] = leavecount
        return result

    elif leaveType_selected == 'work_from_home' :
        if newJoineeValidation(user, fromDate):
            result['errors'] = "You are not allowed to take work from home during first 90 days from you DOJ"
            return result

        else:
            result['success'] = leavecount
            return result

    elif newJoineeValidation(user, fromDate) and leavecount + approvedLeave_newjoinee > 2 :
        result['errors'] = "You are not allowed to take more than two days of leave during first 90 days from your date of joining."
        return result



    else:
        if leaveType_selected == 'sick_leave' and leavecount > 2 and not attachment:
            result['errors'] = "Please attach the necessary medical certificate."
            return result

        else:
            result_temp = validation_month_wise(fromDate, toDate, fromSession, toSession, leavecount, leaveType, user, leave_form)
            if result_temp['success']:
                result['success'] = leavecount
                return result
            else:
                result['errors'] = result_temp['errors']
                return result





def validation_month_wise(fromDate, toDate, fromSession, toSession, leavecount, leaveType, user, leave_form):
    result = {'errors' : [], 'success':[]}
    if fromDate.month != toDate.month:
        last_day = getLast_day_of_month(fromDate)
        first_day = getStart_day_of_month(toDate)
        leave_count_start_month = leave_calculation(fromDate, last_day, fromSession, 'session_second', leaveType)
        leave_count_end_month = leave_calculation(first_day, toDate, 'session_first', toSession, leaveType)
        leaveTotal1 = getLeaveBalance(leaveType, last_day.month, user)
        leaveTotal2 = getLeaveBalance(leaveType, first_day.month, user)

        leaveapproved1 = getLeaveApproved(user, getLast_day_of_month(last_day), leaveType)
        leaveapproved2 = getLeaveApproved(user, getLast_day_of_month(first_day), leaveType)
        balanceLeave1 = leaveTotal1 - leaveapproved1
        balanceLeave2 = leaveTotal2 - leaveapproved2
        if balanceLeave1 >= leave_count_start_month and balanceLeave2 >= leave_count_end_month:
            result['success'] = 'success'

        else :
            result['errors'] = " You do not have the necessary leave balance to avail of this leave."

    else:
        leaveTotal = getLeaveBalance(leaveType, fromDate.month, user)
        leaveapproved = getLeaveApproved(user, getLast_day_of_month(toDate), leaveType)
        balanceLeave = leaveTotal - leaveapproved
        if balanceLeave >= leavecount :
            result['success'] = 'success'
        else :
            result['errors'] = " You do not have the necessary leave balance to avail of this leave."

    return result





def getLast_day_of_month(date):
    if date.month == 12:
        return date.replace(day=31)
    return date.replace(month=date.month+1, day=1) - timedelta(days=1)




def getStart_day_of_month(date):
    return date.replace(day=1)



def leave_calculation(fromdate, todate, fromsession, tosession, leaveType):
    ''' Calculaton for number of leaves accoeding to selected dated and sessions'''
    holiday = Holiday.objects.all().values('date')
    holiday_in_leave = 0
    leavecount = 0
    leave_allowed_on_holiday = ['sabbatical', 'pay_off', 'comp_off_earned', 'maternity_leave']
    leavecount_dummy = 0
    if leaveType not in leave_allowed_on_holiday:
        for leave in holiday:
            if leave['date'] >= fromdate and leave['date'] <= todate and leave['date'].strftime("%A") not in ("Saturday", "Sunday"):
                holiday_in_leave = holiday_in_leave + 1
            if fromsession=='session_second' and fromdate == leave['date'] and leave['date'].strftime("%A") not in ("Saturday", "Sunday"):
                leavecount_dummy=leavecount+.5
            if tosession == 'session_first' and todate == leave['date'] and leave['date'].strftime("%A") not in ("Saturday", "Sunday"):
                leavecount_dummy=leavecount+.5

        daygenerator = (fromdate + timedelta(x + 1) for x in xrange(-1, (todate - fromdate).days))
        leavecount = sum(1 for day in daygenerator if day.weekday() < 5) - holiday_in_leave
    else:
        leavecount = (todate - fromdate).days + 1
    if fromsession=='session_second' and fromdate.strftime("%A") not in ("Saturday", "Sunday") :
        leavecount=leavecount-.5
    if tosession == 'session_first' and todate.strftime("%A") not in ("Saturday", "Sunday"):
        leavecount=leavecount-.5
    leavecount=leavecount + leavecount_dummy
    return leavecount





#calculating leave avail by a user
def getLeaveApproved(user, last_day = None, leaveType = None):
    ''' get all approved leaves '''
    leavecount=0
    year = date.today().year
    newYearDate = date(year, 1, 1)
    if last_day and leaveType:
        if leaveType.leave_type in ['comp_off_earned', 'pay_off']:
            leaves = LeaveApplications.objects.filter(user = user, from_date=last_day, status__in=['approved', 'open'],
            leave_type = leaveType).values('from_date', 'to_date', 'from_session', 'to_session')
        elif leaveType.leave_type == 'comp_off_avail':
            leaves = LeaveSummary.objects.filter(user = user, leave_type = LeaveType.objects.get(leave_type='comp_off_avail'),  year = date.today().year).values('balance')
            if leaves:
                leavecount = leaves[0]['balance']
            return leavecount
        else:
            #leavecheck = ['earned_leave', 'sick_leave', 'casual_leave', 'bereavement_leave', 'maternity_leave', 'paternity_leave' ]
            leaves = LeaveApplications.objects.filter(user = user, from_date__lte=last_day, from_date__gte=newYearDate,
             status__in=['approved', 'open'], leave_type = leaveType).values('from_date', 'to_date', 'from_session', 'to_session')
        for leave in leaves:
            if leave['to_date'] > last_day:
                leavecount = leavecount + leave_calculation(leave['from_date'], last_day, leave['from_session'], leave['to_session'], leaveType)

            else:
                leavecount = leavecount + leave_calculation(leave['from_date'], leave['to_date'], leave['from_session'], leave['to_session'], leaveType)
    else:
        leaves = LeaveApplications.objects.filter(user = user,status__in=['approved', 'open'],
         leave_type__in = LeaveType.objects.filter(leave_type__in=['earned_leave', 'sick_leave', 'casual_leave']) ).values('from_date', 'to_date', 'from_session', 'to_session', 'leave_type__leave_type')
        for leave in leaves:
            leavecount = leavecount + leave_calculation(leave['from_date'], leave['to_date'], leave['from_session'], leave['to_session'], leave['leave_type__leave_type'])
    return leavecount




#calculting leave awarded to user
def getLeaveBalance(leavetype, endmonth, user):
    ''' getting leave for every month'''
    joined_date = Employee.objects.filter(user_id=user).values('joined')
    joined_year = joined_date[0]['joined'].year
    joined_month = joined_date[0]['joined'].month
    joined_day = joined_date[0]['joined'].day
    current_year = date.today().year
    leaveTotal = 0
    leaveType=LeaveType.objects.get(leave_type=leavetype)
    if current_year == joined_year:
        if leaveType.carry_forward == 'yearly':
            leaveTotal = leaveTotal + float((leaveType.count).encode('utf-8')) * (endmonth-joined_month)
            if endmonth != joined_month:
                day_worked = 30 - joined_day
                if day_worked>=28:
                    leaveTotal = leaveTotal + 1.5
                elif day_worked>=20:
                    leaveTotal = leaveTotal + 1
                elif day_worked>=10:
                    leaveTotal = leaveTotal + 0.5
        elif leaveType.carry_forward == 'monthly':
            day_worked = 30 - joined_day
            leaveTotal = leaveTotal + float((leaveType.count).encode('utf-8')) * (endmonth-joined_month)
            if endmonth != joined_month:
                if day_worked>=25:
                    leaveTotal = leaveTotal + .5
        else:
            leaveTotal = leaveTotal + float((leaveType.count).encode('utf-8'))


    else:
        if leaveType.carry_forward == 'yearly':
            balnce_of_last_year = LeaveSummary.objects.filter(leave_type = leaveType, year = current_year-1).values('balance')
            if balnce_of_last_year:
                leaveTotal = leaveTotal + float((balnce_of_last_year[0]['balance']).encode('utf-8'))
            leaveTotal = leaveTotal + float((leaveType.count).encode('utf-8')) * (endmonth+1)
        elif leaveType.carry_forward == 'monthly':
            leaveTotal = leaveTotal + float((leaveType.count).encode('utf-8')) * (endmonth+1)
        else:
            leaveTotal = leaveTotal + float((leaveType.count).encode('utf-8'))
    return leaveTotal


def newJoineeValidation(user, from_date = None):
    joined_date = Employee.objects.filter(user_id=user).values('joined')
    if from_date:
        check_date = from_date
    else:
        check_date = date.today()
    days_of_joined = (check_date - joined_date[0]['joined']).days
    if days_of_joined<80:
        return True
    else:
        return False


def date_by_adding_business_days(from_date, add_days,holidays, leaveType_selected):
    current_date = from_date
    if current_date in [holiday['date'] for holiday in holidays] or current_date.weekday()>=5:
        business_days_to_add = add_days
    else:
        business_days_to_add = add_days-1
    while business_days_to_add > 0:
        current_date += timedelta(days=1)
        weekday = current_date.weekday()
        if leaveType_selected != 'maternity_leave':
            if weekday >= 5:
                continue
            if current_date in [holiday['date'] for holiday in holidays]:
                continue
        business_days_to_add -= 1
    return current_date


def leaveCheckBetweenAppliedLied(leavelist, leave_form):
    flag = False
    if leavelist:
        leave = leavelist[0]
        leave_fromdate = leave.from_date
        leave_todate = leave.to_date
        leave_fromsession = leave.from_session
        leave_tosession = leave.to_session
        fromdate = leave_form.cleaned_data['fromDate']
        todate = leave_form.cleaned_data['toDate']
        fromSession = leave_form.cleaned_data['from_session']
        toSession = leave_form.cleaned_data['to_session']
        if fromdate == leave_todate:
            if leave_tosession == 'session_first' and fromSession == 'session_second':
                flag = False
            elif leave_fromsession == 'session_second' and toSession == 'session_first':
                flag = False
            else:
                flag = True
        elif todate == leave_fromdate:
            if leave_tosession == 'session_first' and fromSession == 'session_second':
                flag = False
            elif leave_fromsession == 'session_second' and toSession == 'session_first':
                flag = False
            else:
                flag = True
        else:
            flag = True
        return flag


def compOffAvailibilityCheck(fromDate, user):
    leaves = LeaveApplications.objects.filter(leave_type__leave_type ='comp_off_earned',
    active =True,
    from_date__lt =fromDate,
    user = user, status = 'approved').order_by('from_date')
    if leaves:
        leaves[0].active= False
        leaves[0].update()
        return False
    return True

def lateLeaveCheck(leave_form, user):
    context ={'error':None}
    fromdate = leave_form.cleaned_data['fromDate']


    if fromdate< date(2016,7,1):
        context['error'] = 'you are applying for past date'
        # fromSession = leave_form.cleaned_data['from_session']
        # todate = leave_form.cleaned_data['toDate']
        # toSession = leave_form.cleaned_data['to_session']
        # leaveType_selected = leave_form.cleaned_data['leave']
        # leavecount = leave_calculation(fromdate, todate, fromSession, toSession, leaveType_selected)
        # emp_id = Employee.objects.get(user_id=user)
        #LateLeaveEmailSendTask.delay(User.objects.get(id=user), emp_id.employee_assigned_id, fromdate, fromSession, todate, toSession, leaveType_selected, leavecount)

    if date.today().day - fromdate.day > 60:
        context['error'] = '60 back limit failing'
    return context
