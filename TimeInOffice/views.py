from django.shortcuts import render, HttpResponse
from django.views.generic import View
from django.shortcuts import render
from django.utils import timezone
from employee.models import Employee, Attendance
from django.contrib import messages
from django.contrib.auth.models import User
import datetime
from datetime import date, timedelta
from datetime import datetime
from django.http import JsonResponse
import json
from calendar import monthrange
from Leave.views import current_week, weekdetail, current_month_week_details, month_in_english, next_week_detail, previous_week_detail


def weekdetail_year(week, month, year):
    currentmontdetail = monthrange(year, month)
    daysinpreviousmonth = currentmontdetail[0]
    startdate = date(year=year,
                                 month=month,
                                 day=1+7*(week-1)) - timedelta(daysinpreviousmonth)
    return startdate

def current_month_week_details_year(no_of_week, month, year):
    weeks_detail = []
    week_detail = [0, 0]
    for val in range(1, no_of_week+1):
        week_detail[0] = weekdetail_year(val, month, year)
        week_detail[1] = week_detail[0] + timedelta(5)
        weeks_detail.append(week_detail)
        week_detail = [0, 0]
    return weeks_detail

def timein(request):

    year = request.GET.get('year')
    if year == '2017':
        if request.user.groups.filter(name__in=['myansrsourcePM']).exists():
            year = 2017
            context = {'weekly_average':[]}
            weekly_avg = []
            weekly_avg_user_list = []
            month = int(request.GET.get('month'))
            user = request.user.id
            manager = Employee.objects.get(user_id=user)
            userlist = Employee.objects.filter(manager_id=manager.employee_assigned_id)
            userid = [user.user_id for user in userlist]
            userid.append(request.user.id)
            userlist = User.objects.filter(id__in=userid, is_active=True)
            context['weekreport'] = weekwisereport(month, userlist)
            current_week_no = int(request.GET.get('week'))
            no_of_week = len(context['weekreport'])
            for user in userlist:
                weekly_avg.append(user.first_name + " " + user.last_name)
                for val in xrange(1, no_of_week + 1):
                    weekly_avg.append(weeklyavg(user, val, month, year))
                weekly_avg_user_list.append(weekly_avg)
                weekly_avg = []
            context['weekly_average'] = weekly_avg_user_list
            context['timereport'] = timereportweeklybasedonuser(month, userlist, current_week_no, year)
            context['current_week_no'] = current_week_no
            context['startdate'] = weekdetail_year(current_week_no, month, year)
            context['enddate'] = context['startdate'] + timedelta(5)
            no_of_avaliable_week = len(context['weekreport'])
            context['current_month_week_details'] = current_month_week_details_year(no_of_avaliable_week, month, year)
            context['month'] = month
            context['month_in_english'] = month_in_english(month)
            context['week_in_english'] = "Week " + str(current_week_no)
            context['next_week'] = next_week_detail(no_of_avaliable_week, current_week_no, month)
            context['year'] = date.today().year
            context['pre_year'] = date.today().year - 1
            if month == 1:
                previous_month_detail = weekwisereport(12, userlist)
            else:
                previous_month_detail = weekwisereport(month - 1, userlist)
            context['previous_week'] = previous_week_detail(len(previous_month_detail), current_week_no, month)
            print context
            return render(request, 'timein_pre_year.html', context)
        else:
            year = 2017
            context = {'weekly_average': []}
            weekly_avg = []
            weekly_avg_user_list = []
            month = int(request.GET.get('month'))
            userlist = User.objects.filter(id=request.user.id, is_active=True)
            context['weekreport'] = weekwisereport(month, userlist)
            current_week_no = int(request.GET.get('week'))
            no_of_week = len(context['weekreport'])
            for user in userlist:
                weekly_avg.append(user.first_name + " " + user.last_name)
                for val in xrange(1, no_of_week + 1):
                    weekly_avg.append(weeklyavg(user, val, month, year))
                weekly_avg_user_list.append(weekly_avg)
                weekly_avg = []
            context['weekly_average'] = weekly_avg_user_list
            context['timereport'] = timereportweeklybasedonuser(month, userlist, current_week_no, year)
            context['current_week_no'] = current_week_no
            context['startdate'] = weekdetail_year(current_week_no, month, year)
            context['enddate'] = context['startdate'] + timedelta(5)
            no_of_avaliable_week = len(context['weekreport'])
            context['current_month_week_details'] = current_month_week_details_year(no_of_avaliable_week, month, year)
            context['month'] = month
            context['month_in_english'] = month_in_english(month)
            context['week_in_english'] = "Week " + str(current_week_no)
            context['next_week'] = next_week_detail(no_of_avaliable_week, current_week_no, month)
            context['year'] = date.today().year
            context['pre_year'] = date.today().year - 1
            if month == 1:
                previous_month_detail = weekwisereport(12, userlist)
            else:
                previous_month_detail = weekwisereport(month - 1, userlist)
            context['previous_week'] = previous_week_detail(len(previous_month_detail), current_week_no, month)
            print context
            return render(request, 'timein_pre_year.html', context)
    else:
        if request.method == 'GET':
            if request.user.groups.filter(name__in=['myansrsourcePM']).exists():
                context = {'weekly_average':[]}
                weekly_avg = []
                weekly_avg_user_list = []
                month = date.today().month
                year = date.today().year
                user = request.user.id
                manager = Employee.objects.get(user_id=user)
                userlist = Employee.objects.filter(manager_id=manager.employee_assigned_id)
                userid = [user.user_id for user in userlist]
                userid.append(request.user.id)
                userlist = User.objects.filter(id__in=userid, is_active=True)
                context['weekreport'] = weekwisereport(month, userlist)
                current_week_no = current_week()
                no_of_week = len(context['weekreport'])
                for user in userlist:
                    weekly_avg.append(user.first_name + " " + user.last_name)
                    for val in xrange(1, no_of_week + 1):
                        weekly_avg.append(weeklyavg(user, val, month, year))
                    weekly_avg_user_list.append(weekly_avg)
                    weekly_avg = []
                context['weekly_average'] = weekly_avg_user_list
                context['timereport'] = timereportweeklybasedonuser(month, userlist, current_week_no, year)
                context['current_week_no'] = current_week_no
                context['startdate'] = weekdetail_year(current_week_no, month, year)
                context['enddate'] = context['startdate'] + timedelta(5)
                no_of_avaliable_week = len(context['weekreport'])
                context['current_month_week_details'] = current_month_week_details_year(no_of_avaliable_week, month, year)
                context['month'] = month
                context['month_in_english'] = month_in_english(month)
                context['week_in_english'] = "Week " + str(current_week_no)
                context['next_week'] = next_week_detail(no_of_avaliable_week, current_week_no, month)
                context['year'] = date.today().year
                context['pre_year'] = date.today().year - 1
                if month == 1:
                    previous_month_detail = weekwisereport(12, userlist)
                else:
                    previous_month_detail = weekwisereport(month - 1, userlist)
                context['previous_week'] = previous_week_detail(len(previous_month_detail), current_week_no, month)
                return render(request, 'timein.html', context)
            else:
                context = {'weekly_average': []}
                weekly_avg = []
                weekly_avg_user_list = []
                month = date.today().month
                year = date.today().year
                user = request.user.id
                userlist = User.objects.filter(id=request.user.id, is_active=True)
                context['weekreport'] = weekwisereport(month, userlist)
                current_week_no = current_week()
                no_of_week = len(context['weekreport'])
                for user in userlist:
                    weekly_avg.append(user.first_name + " " + user.last_name)
                    for val in xrange(1, no_of_week + 1):
                        weekly_avg.append(weeklyavg(user, val, month, year))
                    weekly_avg_user_list.append(weekly_avg)
                    weekly_avg = []
                context['weekly_average'] = weekly_avg_user_list
                context['timereport'] = timereportweeklybasedonuser(month, userlist, current_week_no, year)
                context['current_week_no'] = current_week_no
                context['startdate'] = weekdetail_year(current_week_no, month, year)
                context['enddate'] = context['startdate'] + timedelta(5)
                no_of_avaliable_week = len(context['weekreport'])
                context['current_month_week_details'] = current_month_week_details_year(no_of_avaliable_week, month,
                                                                                        year)
                context['month'] = month
                context['month_in_english'] = month_in_english(month)
                context['week_in_english'] = "Week " + str(current_week_no)
                context['next_week'] = next_week_detail(no_of_avaliable_week, current_week_no, month)
                context['year'] = date.today().year
                context['pre_year'] = date.today().year - 1
                if month == 1:
                    previous_month_detail = weekwisereport(12, userlist)
                else:
                    previous_month_detail = weekwisereport(month - 1, userlist)
                context['previous_week'] = previous_week_detail(len(previous_month_detail), current_week_no, month)
                return render(request, 'timein.html', context)

def timereportweeklybasedonuser(month, userlist, week, year):
    weekreport = []
    userdata = []
    for user in userlist:
        userdata.append(user.first_name + " " + user.last_name)
        userdata.append(userweeklytimereport(user, week, month, year))
        week_avg = weeklyavg(user, week, month, year)
        userdata.append(week_avg)
        weekreport.append(userdata)
        userdata = []
    return weekreport

# returns hours for each day for a user for a week
def userweeklytimereport(user, week, month, year):
    timelist = []
    startdate = weekdetail_year(week, month, year)
    enddate = startdate + timedelta(5)
    for single_date in daterange(startdate, enddate):
        time_detail = timecheck(user, single_date)
        timelist.append(time_detail)
    return timelist

def weeklyavg(user, week, month, year):
    total_avg = []
    total = userweeklytimereport(user, week, month, year)
    for time in total:
        if time == 0:
            pass
        elif time is not None:
            total_avg.append(time)
    if sum(total_avg) == 0:
        avg = 0
    else:
        avg = sum(total_avg)/len(total_avg)

    return round(avg, 2)

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def timecheck(user, date):
    att_day = 0
    userattendance = Attendance.objects.filter(employee_id=user.employee.employee_assigned_id, attdate=date)
    if not userattendance:
        att_day = 0
    for att in userattendance:
        # print type(att.swipe_out)
        # print type(att.swipe_in)
        if att.swipe_out and att.swipe_in is not None:
            att_day = att.swipe_out - att.swipe_in
            delta = att_day
            sec = delta.seconds
            hours = sec // 3600
            minutes = (sec // 60) - (hours * 60)
            att_day = ('{0}.{1}'.format(hours, minutes))
            att_day = float(att_day)
        return round(att_day, 2)

def weekwisedata(request):
    if request.user.groups.filter(name__in=['myansrsourcePM']).exists():
        context = {}
        week = int(request.GET.get('week'))
        month = int(request.GET.get('month'))
        year = int(request.GET.get('year'))
        user = request.user.id
        manager = Employee.objects.get(user_id=user)
        userlist = Employee.objects.filter(manager_id=manager.employee_assigned_id)
        userid = [user.user_id for user in userlist]
        userid.append(request.user.id)
        userlist = User.objects.filter(id__in=userid, is_active=True)
        context['weekreport'] = weekwisereport(month, userlist)
        context['timereport'] = timereportweeklybasedonuser(month, userlist, week, year)
        no_of_avaliable_week = len(context['weekreport'])
        context['current_month_week_details'] = current_month_week_details_year(no_of_avaliable_week, month, year)
        context['startdate'] = weekdetail_year(week, month, year)
        context['enddate'] = context['startdate'] + timedelta(5)
        context['month'] = month
        context['month_in_english'] = month_in_english(month)
        context['next_week'] = next_week_detail(no_of_avaliable_week, week, month)
        if month == 1:
            previous_month_detail = weekwisereport(12, userlist)
        else:
            previous_month_detail = weekwisereport(month-1, userlist)
        context['previous_week'] = previous_week_detail(len(previous_month_detail), week, month)
        context['current_week_no'] = week
        context['week_in_english'] = "Week " + str(week)
        context['year'] = date.today().year
        context['pre_year'] = date.today().year - 1
        return render(request, 'timeweeklyreport.html', context)
    else:
        context = {}
        week = int(request.GET.get('week'))
        month = int(request.GET.get('month'))
        year = int(request.GET.get('year'))
        userlist = User.objects.filter(id=request.user.id, is_active=True)
        context['weekreport'] = weekwisereport(month, userlist)
        context['timereport'] = timereportweeklybasedonuser(month, userlist, week, year)
        no_of_avaliable_week = len(context['weekreport'])
        context['current_month_week_details'] = current_month_week_details_year(no_of_avaliable_week, month, year)
        context['startdate'] = weekdetail_year(week, month, year)
        context['enddate'] = context['startdate'] + timedelta(5)
        context['month'] = month
        context['month_in_english'] = month_in_english(month)
        context['next_week'] = next_week_detail(no_of_avaliable_week, week, month)
        if month == 1:
            previous_month_detail = weekwisereport(12, userlist)
        else:
            previous_month_detail = weekwisereport(month - 1, userlist)
        context['previous_week'] = previous_week_detail(len(previous_month_detail), week, month)
        context['current_week_no'] = week
        context['week_in_english'] = "Week " + str(week)
        context['year'] = date.today().year
        context['pre_year'] = date.today().year - 1
        return render(request, 'timeweeklyreport.html', context)

def monthwisedata(request):
    if request.user.groups.filter(name__in=['myansrsourcePM']).exists():
        month = int(request.GET.get('month'))
        year = int(request.GET.get('year'))
        context = {'weekly_average': []}
        weekly_avg = []
        weekly_avg_user_list = []
        user = request.user.id
        manager = Employee.objects.get(user_id=user)
        userlist = Employee.objects.filter(manager_id=manager.employee_assigned_id)
        userid = [user.user_id for user in userlist]
        userid.append(request.user.id)
        userlist = User.objects.filter(id__in=userid, is_active=True)
        current_week_no = current_week()
        context['weekreport'] = weekwisereport(month, userlist)
        no_of_week = len(context['weekreport'])
        for user in userlist:
            weekly_avg.append(user.first_name + " " + user.last_name)
            for val in xrange(1, no_of_week + 1):
                weekly_avg.append(weeklyavg(user, val, month, year))
            weekly_avg_user_list.append(weekly_avg)
            weekly_avg = []
        context['weekly_average'] = weekly_avg_user_list
        context['timereport'] = timereportweeklybasedonuser(month, userlist, current_week_no, year)
        context['startdate'] = weekdetail_year(current_week_no, month, year)
        context['enddate'] = context['startdate'] + timedelta(5)
        context['year'] = date.today().year
        context['pre_year'] = date.today().year - 1
        return render(request, 'timemonthlyreport.html', context)
    else:
        month = int(request.GET.get('month'))
        year = int(request.GET.get('year'))
        context = {'weekly_average': []}
        weekly_avg = []
        weekly_avg_user_list = []
        userlist = User.objects.filter(id=request.user.id, is_active=True)
        current_week_no = current_week()
        context['weekreport'] = weekwisereport(month, userlist)
        no_of_week = len(context['weekreport'])
        for user in userlist:
            weekly_avg.append(user.first_name + " " + user.last_name)
            for val in xrange(1, no_of_week + 1):
                weekly_avg.append(weeklyavg(user, val, month, year))
            weekly_avg_user_list.append(weekly_avg)
            weekly_avg = []
        context['weekly_average'] = weekly_avg_user_list
        context['timereport'] = timereportweeklybasedonuser(month, userlist, current_week_no, year)
        context['startdate'] = weekdetail_year(current_week_no, month, year)
        context['enddate'] = context['startdate'] + timedelta(5)
        context['year'] = date.today().year
        context['pre_year'] = date.today().year - 1
        return render(request, 'timemonthlyreport.html', context)

def weekwisereport(month, userlist):
    weekreport = []
    weekreportdetail = {}
    currentmontdetail = monthrange(date.today().year, month)
    if month == 1:
        previousmontdetail = monthrange(date.today().year, 12)
    else:
        previousmontdetail = monthrange(date.today().year, month - 1)

    previousmonthdays = previousmontdetail[1]
    dayscount = currentmontdetail[1]
    above9 = 0
    below6 = 0
    between68 = 0
    between89 = 0
    for val in range(0, currentmontdetail[0]):
        if currentmontdetail[0] == 6 and val == 0:
            pass
        else:
            if month == 1:
                datecheck = date(year=date.today().year - 1, month=12, day=previousmonthdays - val)
            else:
                datecheck = date(year=date.today().year, month=month - 1, day=previousmonthdays - val)

    if currentmontdetail[0] == 6:
        weekreportdetail['above9'] = above9
        weekreportdetail['below6'] = below6
        weekreportdetail['between68'] = between68
        weekreportdetail['between89'] = between89
        weekreport.append(weekreportdetail)
        above9 = 0
        below6 = 0
        between68 = 0
        between89 = 0
        weekreportdetail = {}

    for val in range(1, dayscount+1):
        date1 = date(year=date.today().year, month=month, day=val)
        if date1.strftime("%A") == 'Saturday':
            weekreportdetail['above9'] = above9
            weekreportdetail['below6'] = below6
            weekreportdetail['between68'] = between68
            weekreportdetail['between89'] = between89
            weekreport.append(weekreportdetail)
            above9 = 0
            below6 = 0
            between68 = 0
            between89 = 0
            weekreportdetail = {}

        elif date1.strftime("%A") == 'Sunday':
            pass
        elif val == dayscount+1:
            weekreportdetail['above9'] = above9
            weekreportdetail['below6'] = below6
            weekreportdetail['between68'] = between68
            weekreportdetail['between89'] = between89
            weekreport.append(weekreportdetail)
            above9 = 0
            below6 = 0
            between68 = 0
            between89 = 0
            weekreportdetail = {}

    return weekreport