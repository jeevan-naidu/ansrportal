from django.forms.util import ErrorList
import json
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.contrib import auth, messages
from django.shortcuts import render
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponse
from MyANSRSource.models import Project, TimeSheetEntry, \
    ProjectMilestone, ProjectTeamMember, Book, ProjectChangeInfo, \
    Chapter
from CompanyMaster.models import Holiday
from MyANSRSource.forms import LoginForm, ProjectBasicInfoForm, \
    ProjectTeamForm, ProjectMilestoneForm, \
    ActivityForm, TimesheetFormset, ProjectFlagForm, \
    ChangeProjectBasicInfoForm, ChangeProjectTeamMemberForm, \
    ChangeProjectMilestoneForm, ChangeProjectForm, \
    CloseProjectMilestoneForm
import CompanyMaster
import employee
from django.contrib.formtools.wizard.views import SessionWizardView
from django.forms.formsets import formset_factory
from datetime import datetime, timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import Q
from django.conf import settings
import re
# views for ansr

FORMS = [
    ("Define Project", ProjectBasicInfoForm),
    ("Basic Information", ProjectFlagForm),
    ("Define Team", formset_factory(
        ProjectTeamForm,
        extra=0,
        can_delete=True
    )),
    ("Financial Milestones", formset_factory(
        ProjectMilestoneForm,
        extra=2,
        can_delete=True
    )),
]
TEMPLATES = {
    "Define Project": "MyANSRSource/projectDefinition.html",
    "Basic Information": "MyANSRSource/projectBasicInfo.html",
    "Define Team": "MyANSRSource/projectTeamMember.html",
    "Financial Milestones": "MyANSRSource/projectMilestone.html",
}

CFORMS = [
    ("My Projects", ChangeProjectForm),
    ("Change Basic Information", ChangeProjectBasicInfoForm),
    ("Change Team Members", formset_factory(
        ChangeProjectTeamMemberForm,
        extra=0,
    )),
    ("Change Milestones", formset_factory(
        ChangeProjectMilestoneForm,
        extra=0,
    )),
]
CTEMPLATES = {
    "My Projects": "MyANSRSource/changeProject.html",
    "Change Basic Information": "MyANSRSource/changeProjectBasicInfo.html",
    "Change Team Members": "MyANSRSource/changeProjectTeamMember.html",
    "Change Milestones": "MyANSRSource/changeProjectMilestone.html",
}

TMFORMS = [
    ("My Projects", ChangeProjectForm),
    ("Close Milestone", formset_factory(
        CloseProjectMilestoneForm,
        extra=0,
    )),
]
TMTEMPLATES = {
    "My Projects": "MyANSRSource/closeProject.html",
    "Close Milestone": "MyANSRSource/closeProjectMilestone.html",
}


def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return checkUser(
                form.cleaned_data['userid'],
                form.cleaned_data['password'],
                request, form)
    else:
        form = LoginForm()
    return loginResponse(request, form, 'MyANSRSource/index.html')


def loginResponse(request, form, template):
    data = {'form': form if form else LoginForm(request.POST), }
    return render(request, template, data)


@login_required
def Timesheet(request):
    # Creating Formset
    tsform = TimesheetFormset(request.user)
    tsFormset = formset_factory(
        tsform, extra=2, can_delete=True
    )
    atFormset = formset_factory(
        ActivityForm, extra=2, can_delete=True
    )
    # Week Calculation.
    today = datetime.now().date()
    minAutoApprove = 36
    maxAutoApprove = 44
    leaveDayWork = False
    weekstartDate = today - timedelta(days=datetime.now().date().weekday())
    ansrEndDate = weekstartDate + timedelta(days=6)
    disabled = 'next'
    # Getting the form values and storing it to DB.
    if request.method == 'POST':
        # Getting the forms with submitted values
        timesheets = tsFormset(request.POST)
        activities = atFormset(request.POST, prefix='at')
        # User values for timsheet
        if timesheets.is_valid() and activities.is_valid():
            changedStartDate = datetime.strptime(
                request.POST.get('startdate'), '%d%m%Y'
            ).date()
            changedEndDate = datetime.strptime(
                request.POST.get('enddate'), '%d%m%Y'
            ).date()
            mondayTotal = 0
            tuesdayTotal = 0
            wednesdayTotal = 0
            thursdayTotal = 0
            fridayTotal = 0
            saturdayTotal = 0
            sundayTotal = 0
            weekTotal = 0
            billableTotal = 0
            nonbillableTotal = 0
            (timesheetList, activitiesList,
             timesheetDict, activityDict) = ([], [], {}, {})
            weekHolidays = Holiday.objects.filter(
                date__range=[changedStartDate, changedEndDate]
            ).values('date')
            for timesheet in timesheets:
                if timesheet.cleaned_data['DELETE'] is True:
                    TimeSheetEntry.objects.filter(
                        id=timesheet.cleaned_data['tsId']
                    ).delete()
                else:
                    for holiday in weekHolidays:
                        holidayDay = '{0}H'.format(
                            holiday['date'].strftime('%A').lower()
                        )
                        if timesheet.cleaned_data[holidayDay] > 0:
                            leaveDayWork = True
                    del(timesheet.cleaned_data['DELETE'])
                    del(timesheet.cleaned_data['monday'])
                    del(timesheet.cleaned_data['tuesday'])
                    del(timesheet.cleaned_data['wednesday'])
                    del(timesheet.cleaned_data['thursday'])
                    del(timesheet.cleaned_data['friday'])
                    del(timesheet.cleaned_data['saturday'])
                    del(timesheet.cleaned_data['sunday'])
                    del(timesheet.cleaned_data['total'])
                    for k, v in timesheet.cleaned_data.iteritems():
                        if k == 'mondayH':
                            mondayTotal += v
                        elif k == 'tuesdayH':
                            tuesdayTotal += v
                        elif k == 'wednesdayH':
                            wednesdayTotal += v
                        elif k == 'thursdayH':
                            thursdayTotal += v
                        elif k == 'fridayH':
                            fridayTotal += v
                        elif k == 'saturdayH':
                            saturdayTotal += v
                        elif k == 'sundayH':
                            sundayTotal += v
                        elif k == 'totalH':
                            billableTotal += v
                            weekTotal += v
                        timesheetDict[k] = v
                    timesheetList.append(timesheetDict.copy())
                    timesheetDict.clear()
            for activity in activities:
                if activity.cleaned_data['DELETE'] is True:
                    TimeSheetEntry.objects.filter(
                        id=activity.cleaned_data['atId']
                    ).delete()
                else:
                    del(activity.cleaned_data['DELETE'])
                    for k, v in activity.cleaned_data.iteritems():
                        if k == 'activity_monday':
                            mondayTotal += v
                        elif k == 'activity_tuesday':
                            tuesdayTotal += v
                        elif k == 'activity_wednesday':
                            wednesdayTotal += v
                        elif k == 'activity_thursday':
                            thursdayTotal += v
                        elif k == 'activity_friday':
                            fridayTotal += v
                        elif k == 'activity_saturday':
                            saturdayTotal += v
                        elif k == 'activity_sunday':
                            sundayTotal += v
                        elif k == 'total':
                            nonbillableTotal += v
                            weekTotal += v
                        activityDict[k] = v
                    activitiesList.append(activityDict.copy())
                    activityDict.clear()
            if (mondayTotal > 24) | (tuesdayTotal > 24) | \
                    (wednesdayTotal > 24) | (thursdayTotal > 24) | \
                    (fridayTotal > 24) | (saturdayTotal > 24) | \
                    (sundayTotal > 24):
                messages.error(request, 'You can only work for 24 hours a day')
            elif (weekTotal < minAutoApprove) | (weekTotal > maxAutoApprove) | \
                 (billableTotal > 44) | (nonbillableTotal > 40) | \
                 (leaveDayWork is True):
                for eachActivity in activitiesList:
                    # Getting objects for models
                    if eachActivity['atId'] > 0:
                        nonbillableTS = TimeSheetEntry.objects.filter(
                            id=eachActivity['atId']
                        )[0]
                    else:
                        nonbillableTS = TimeSheetEntry()
                    # Common values for Billable and Non-Billable
                    nonbillableTS.wkstart = changedStartDate
                    nonbillableTS.wkend = changedEndDate
                    nonbillableTS.teamMember = request.user
                    nonbillableTS.hold = True
                    if (weekTotal < minAutoApprove) | \
                            (weekTotal > maxAutoApprove):
                        nonbillableTS.exception = \
                            '10% deviation in totalhours for this week'
                    elif nonbillableTotal > 40:
                        nonbillableTS.exception = \
                            'NonBillable activity more than 40 Hours'
                    for k, v in eachActivity.iteritems():
                        if k == 'activity_monday':
                            nonbillableTS.mondayH = v
                        elif k == 'activity_tuesday':
                            nonbillableTS.tuesdayH = v
                        elif k == 'activity_wednesday':
                            nonbillableTS.wednesdayH = v
                        elif k == 'activity_thursday':
                            nonbillableTS.thursdayH = v
                        elif k == 'activity_friday':
                            nonbillableTS.fridayH = v
                        elif k == 'activity_saturday':
                            nonbillableTS.saturdayH = v
                        elif k == 'activity_sunday':
                            nonbillableTS.sundayH = v
                        elif k == 'activity_total':
                            nonbillableTS.totalH = v
                        elif k == 'activity_feedback':
                            nonbillableTS.feedback = v
                        elif k == 'activity':
                            nonbillableTS.activity = v
                    nonbillableTS.save()
                for eachTimesheet in timesheetList:
                    if eachTimesheet['tsId'] > 0:
                        billableTS = TimeSheetEntry.objects.filter(
                            id=eachTimesheet['tsId']
                        )[0]
                    else:
                        billableTS = TimeSheetEntry()
                    billableTS.wkstart = changedStartDate
                    billableTS.wkend = changedEndDate
                    billableTS.teamMember = request.user
                    billableTS.billable = True
                    billableTS.hold = True
                    if (weekTotal < minAutoApprove) | \
                            (weekTotal > maxAutoApprove):
                        billableTS.exception = \
                            '10% deviation in totalhours for this week'
                    elif billableTotal > 40:
                        billableTS.exception = \
                            'Billable activity more than 40 Hours'
                    elif leaveDayWork is True:
                        billableTS.exception = 'Worked on Holiday'
                    for k, v in eachTimesheet.iteritems():
                        setattr(billableTS, k, v)
                    billableTS.save()
            else:
                # Save Timesheet
                for eachActivity in activitiesList:
                    # Getting objects for models
                    if eachActivity['atId'] > 0:
                        nonbillableTS = TimeSheetEntry.objects.filter(
                            id=eachActivity['atId']
                        )[0]
                    else:
                        nonbillableTS = TimeSheetEntry()
                    # Common values for Billable and Non-Billable
                    nonbillableTS.wkstart = changedStartDate
                    nonbillableTS.wkend = changedEndDate
                    nonbillableTS.activity = activity
                    nonbillableTS.teamMember = request.user
                    nonbillableTS.approved = True
                    nonbillableTS.hold = True
                    nonbillableTS.approvedon = datetime.now()
                    for k, v in eachActivity.iteritems():
                        setattr(nonbillableTS, k, v)
                    nonbillableTS.save()
                for eachTimesheet in timesheetList:
                    if eachTimesheet['tsId'] > 0:
                        billableTS = TimeSheetEntry.objects.filter(
                            id=eachTimesheet['tsId']
                        )[0]
                    else:
                        billableTS = TimeSheetEntry()
                    billableTS.wkstart = changedStartDate
                    billableTS.wkend = changedEndDate
                    billableTS.teamMember = request.user
                    billableTS.billable = True
                    billableTS.approved = True
                    billableTS.approvedon = datetime.now()
                    billableTS.hold = True
                    for k, v in eachTimesheet.iteritems():
                        setattr(billableTS, k, v)
                    billableTS.save()
            return HttpResponseRedirect(request.get_full_path())
        else:
            if request.GET.get('week') == 'prev':
                weekstartDate = datetime.strptime(
                    request.GET.get('startdate'), '%d%m%Y'
                ).date() - timedelta(days=7)
                ansrEndDate = datetime.strptime(
                    request.GET.get('enddate'), '%d%m%Y'
                ).date() - timedelta(days=7)
                disabled = 'prev'
            elif request.GET.get('week') == 'next':
                disabled = 'next'
            tsErrorList = timesheets.errors
            tsError = [k.cleaned_data for k in timesheets]
            for eachErrorData in tsError:
                for k, v in eachErrorData.iteritems():
                    if k == 'project':
                        ptype = Project.objects.filter(
                            id=eachErrorData['project'].id
                        ).values('projectType')[0]['projectType']
                        eachErrorData['projectType'] = ptype
            atError = [k for k in activities.cleaned_data]
            tsFormset = formset_factory(tsform,
                                        extra=0,
                                        can_delete=True)
            tsFormset = tsFormset(initial=tsError)
            atFormset = formset_factory(ActivityForm,
                                        extra=0,
                                        can_delete=True)
            atFormset = atFormset(initial=atError, prefix='at')
            data = {'weekstartDate': weekstartDate,
                    'weekendDate': ansrEndDate,
                    'disabled': disabled,
                    'ErrorList': tsErrorList,
                    'shortDays': ['Mon', 'Tue', 'Wed', 'Thu',
                                  'Fri', 'Sat', 'Sun'],
                    'tsFormset': tsFormset,
                    'hold': False,
                    'atFormset': atFormset}
            return render(request, 'MyANSRSource/timesheetEntry.html', data)
    else:
        if request.GET.get('week') == 'prev':
            weekstartDate = datetime.strptime(
                request.GET.get('startdate'), '%d%m%Y'
            ).date() - timedelta(days=7)
            ansrEndDate = datetime.strptime(
                request.GET.get('enddate'), '%d%m%Y'
            ).date() - timedelta(days=7)
            disabled = 'prev'
        elif request.GET.get('week') == 'next':
            disabled = 'next'
        # Creating data for templates
        cwTimesheet = TimeSheetEntry.objects.filter(
            wkstart=weekstartDate, wkend=ansrEndDate,
            teamMember=request.user,
            approved=False, activity__isnull=True
        ).count()
        cwActivityData = TimeSheetEntry.objects.filter(
            Q(
                wkstart=weekstartDate,
                wkend=ansrEndDate,
                teamMember=request.user,
                approved=False,
                project__isnull=True
            )
        ).values('id', 'activity', 'mondayH', 'tuesdayH', 'wednesdayH',
                 'thursdayH', 'fridayH', 'saturdayH', 'sundayH', 'totalH',
                 'managerFeedback'
                 )
        cwTimesheetData = TimeSheetEntry.objects.filter(
            Q(
                wkstart=weekstartDate,
                wkend=ansrEndDate,
                teamMember=request.user,
                approved=False,
                activity__isnull=True
            )
        ).values('id', 'project', 'location', 'chapter', 'task', 'mondayH',
                 'mondayQ', 'tuesdayQ', 'tuesdayH', 'wednesdayQ', 'wednesdayH',
                 'thursdayH', 'thursdayQ', 'fridayH', 'fridayQ', 'hold',
                 'saturdayH', 'saturdayQ', 'sundayH', 'sundayQ',
                 'totalH', 'totalQ', 'managerFeedback', 'project__projectType'
                 )
        tsData = {}
        tsDataList = []
        for eachData in cwTimesheetData:
            for k, v in eachData.iteritems():
                tsData[k] = v
                if k == 'managerFeedback':
                    tsData['feedback'] = v
                if k == 'id':
                    tsData['tsId'] = v
                if k == 'project__projectType':
                    tsData['projectType'] = v
            tsDataList.append(tsData.copy())
            tsData.clear()
        atData = {}
        atDataList = []
        for eachData in cwActivityData:
            for k, v in eachData.iteritems():
                if 'monday' in k:
                    atData['activity_monday'] = v
                if 'tuesday' in k:
                    atData['activity_tuesday'] = v
                if 'wednesday' in k:
                    atData['activity_wednesday'] = v
                if 'thursday' in k:
                    atData['activity_thursday'] = v
                if 'friday' in k:
                    atData['activity_friday'] = v
                if 'saturday' in k:
                    atData['activity_saturday'] = v
                if 'sunday' in k:
                    atData['activity_sunday'] = v
                if 'total' in k:
                    atData['activity_total'] = v
                if k == 'managerFeedback':
                    atData['feedback'] = v
                if k == 'id':
                    atData['atId'] = v
            atDataList.append(atData.copy())
            atData.clear()
        if cwTimesheet > 0:
            tsFormset = formset_factory(tsform,
                                        extra=0,
                                        can_delete=True)
            tsFormset = tsFormset(initial=tsDataList)
            atFormset = formset_factory(ActivityForm,
                                        extra=0,
                                        can_delete=True)
            atFormset = atFormset(initial=atDataList, prefix='at')
        else:
            tsFormset = formset_factory(tsform,
                                        extra=2,
                                        can_delete=True)
            atFormset = formset_factory(ActivityForm,
                                        extra=2,
                                        can_delete=True)
            atFormset = atFormset(prefix='at')
        cwApprovedTimesheet = TimeSheetEntry.objects.filter(
            wkstart=weekstartDate, wkend=ansrEndDate,
            teamMember=request.user,
            approved=True
        ).count()
        cwApprovedActivityData = TimeSheetEntry.objects.filter(
            Q(
                wkstart=weekstartDate,
                wkend=ansrEndDate,
                teamMember=request.user,
                approved=True,
                project__isnull=True
            )
        ).values('activity', 'mondayH', 'tuesdayH', 'wednesdayH', 'thursdayH',
                 'fridayH', 'saturdayH', 'sundayH', 'totalH', 'managerFeedback'
                 )
        cwApprovedTimesheetData = TimeSheetEntry.objects.filter(
            Q(
                wkstart=weekstartDate,
                wkend=ansrEndDate,
                teamMember=request.user,
                approved=True,
                activity__isnull=True
            )
        ).values('project__name', 'location__name', 'chapter__name', 'mondayH',
                 'tuesdayH', 'wednesdayH', 'thursdayH', 'task',
                 'fridayH', 'saturdayH', 'sundayH', 'totalH', 'managerFeedback'
                 )
        billableHours = TimeSheetEntry.objects.filter(
            Q(
                wkstart=weekstartDate,
                wkend=ansrEndDate,
                teamMember=request.user,
                approved=False,
                activity__isnull=True
            ),
            ~Q(task='I')
        ).values('totalH')
        idleHours = TimeSheetEntry.objects.filter(
            Q(
                wkstart=weekstartDate,
                wkend=ansrEndDate,
                task='I',
                teamMember=request.user,
                approved=False,
                activity__isnull=True
            ),
        ).values('totalH')
        othersHours = TimeSheetEntry.objects.filter(
            Q(
                wkstart=weekstartDate,
                wkend=ansrEndDate,
                teamMember=request.user,
                approved=False,
                project__isnull=True
            ),
        ).values('totalH')
        bTotal = 0
        for billable in billableHours:
            bTotal += billable['totalH']
        idleTotal = 0
        for idle in idleHours:
            idleTotal += idle['totalH']
        othersTotal = 0
        for others in othersHours:
            othersTotal += others['totalH']
        if cwApprovedTimesheet > 0:
            messages.success(request, 'Timesheet is approved for this week')
            data = {'weekstartDate': weekstartDate,
                    'weekendDate': ansrEndDate,
                    'disabled': disabled,
                    'currentTimesheet': cwApprovedTimesheetData,
                    'currentActivity': cwApprovedActivityData
                    }
            return render(request, 'MyANSRSource/timesheetApproved.html', data)
        else:
            if cwTimesheet > 0:
                hold = cwTimesheetData[0]['hold']
                if hold is True:
                    messages.warning(request,
                                     'This timesheet is sent for approval \
                                     to your manager')
                else:
                    messages.warning(request,
                                     'Your manager kept this timesheet on hold, \
                                     please resubmit')
            else:
                messages.info(request,
                              'Please fill timesheet for this week')
                hold = False
            data = {'weekstartDate': weekstartDate,
                    'weekendDate': ansrEndDate,
                    'disabled': disabled,
                    'tsFormset': tsFormset,
                    'hold': hold,
                    'shortDays': ['Mon', 'Tue', 'Wed', 'Thu',
                                  'Fri', 'Sat', 'Sun'],
                    'billableHours': billableHours,
                    'idleHours': idleHours,
                    'bTotal': bTotal,
                    'idleTotal': idleTotal,
                    'othersTotal': othersTotal,
                    'atFormset': atFormset}
            return render(request, 'MyANSRSource/timesheetEntry.html', data)


@login_required
def ApproveTimesheet(request):
    if request.method == 'POST':
        for k, v in request.POST.iteritems():
            if 'feedback' in k:
                updateRec = k.split('-', 1)[1]
                TimeSheetEntry.objects.filter(
                    id=updateRec
                ).update(managerFeedback=v)
            elif 'status' in k:
                updateRec = k.split('-', 1)[1]
                if v == 'approve':
                    TimeSheetEntry.objects.filter(
                        id=updateRec
                    ).update(approved=True, approvedon=datetime.now())
                else:
                    TimeSheetEntry.objects.filter(
                        id=updateRec
                    ).update(hold=False)
        return HttpResponseRedirect('/myansrsource/dashboard')
    else:
        unApprovedTimeSheet = TimeSheetEntry.objects.filter(
            project__projectManager=request.user,
            approved=False
        ).values('id', 'project__id', 'project__name', 'wkstart', 'wkend',
                 'teamMember__username', 'totalH', 'exception', 'approved',
                 'managerFeedback').order_by('project__id')

        data = {
            'timesheetInfo': unApprovedTimeSheet
        }
        return render(request, 'MyANSRSource/timesheetApprove.html', data)


@login_required
def Dashboard(request):
    if request.session['usertype'] == 'pm':
        totalActiveProjects = Project.objects.filter(
            projectManager=request.user,
            closed=False
        ).count()
        unApprovedTimeSheet = TimeSheetEntry.objects.filter(
            project__projectManager=request.user,
            approved=False
        ).count()
        totalEmployees = User.objects.all().count()
        activeMilestones = ProjectMilestone.objects.filter(
            project__projectManager=request.user,
            project__closed=False,
            closed=False
        ).count()
    else:
        totalActiveProjects = 0
        unApprovedTimeSheet = 0
        totalEmployees = 0
        activeMilestones = 0
    billableProjects = ProjectTeamMember.objects.filter(
        project__closed=False,
        member=request.user,
        project__internal=False
    ).count()
    currentProjects = ProjectTeamMember.objects.filter(
        project__closed=False,
        member=request.user,
        project__startDate__lte=datetime.now(),
        project__endDate__gte=datetime.now()
    ).values('project__name', 'project__endDate')
    futureProjects = ProjectTeamMember.objects.filter(
        project__closed=False,
        member=request.user,
        project__startDate__gte=datetime.now()
    ).values('project__name', 'project__startDate')
    for eachProject in futureProjects:
        today = datetime.now()
        projectDate = eachProject['project__startDate']
        dayDiff = projectDate.day - today.day
        monthDiff = projectDate.month - today.month
        yearDiff = projectDate.year - today.year
        eachProject['dayDiff'] = str(abs(dayDiff)).zfill(2)
        eachProject['monthDiff'] = str(abs(monthDiff)).zfill(2)
        eachProject['yearDiff'] = abs(yearDiff)
        del eachProject['project__startDate']
    for eachProject in currentProjects:
        today = datetime.now()
        projectDate = eachProject['project__endDate']
        dayDiff = projectDate.day - today.day
        monthDiff = projectDate.month - today.month
        yearDiff = projectDate.year - today.year
        eachProject['dayDiff'] = str(abs(dayDiff)).zfill(2)
        eachProject['monthDiff'] = str(abs(monthDiff)).zfill(2)
        eachProject['yearDiff'] = abs(yearDiff)
        del eachProject['project__endDate']
    myprojects = ProjectTeamMember.objects.filter(
        project__closed=False,
        member=request.user
    ).values('project__name', 'project__startDate', 'project__endDate')
    for eachProject in myprojects:
        eachProject['project__startDate'] = eachProject[
            'project__startDate'
        ].strftime('%Y-%m-%d')
        eachProject['project__endDate'] = eachProject[
            'project__endDate'
        ].strftime('%Y-%m-%d')
    holidayList = Holiday.objects.all().values('name', 'date')
    for eachHoliday in holidayList:
        eachHoliday['date'] = eachHoliday['date'].strftime('%Y-%m-%d')
    data = {
        'username': request.session['username'],
        'usertype': request.session['usertype'],
        'holidayList': holidayList,
        'projectsList': myprojects,
        'billableProjects': billableProjects,
        'currentProjects': currentProjects,
        'futureProjects': futureProjects,
        'activeProjects': totalActiveProjects,
        'activeMilestones': activeMilestones,
        'unapprovedts': unApprovedTimeSheet,
        'totalemp': totalEmployees
    }
    return render(request, 'MyANSRSource/landingPage.html', data)


def checkUser(userName, password, request, form):
    user = authenticate(username=userName, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            try:
                if user.groups.all()[0].name == "project manager":
                    request.session['username'] = userName
                    request.session['usertype'] = 'pm'
                    return HttpResponseRedirect('dashboard')
                elif user.groups.all()[0].name == "project team":
                    request.session['username'] = userName
                    request.session['usertype'] = 'tm'
                    return HttpResponseRedirect('dashboard')
            except IndexError:
                messages.error(request, 'This user does not have access.')
                return loginResponse(request, form, 'MyANSRSource/index.html')
        else:
            messages.error(request, 'Sorry this user is not active')
            return loginResponse(request, form, 'MyANSRSource/index.html')
    else:
        messages.error(request, 'Sorry login failed')
        return loginResponse(request, form, 'MyANSRSource/index.html')


class TrackMilestoneWizard(SessionWizardView):

    def get_template_names(self):
        return [TMTEMPLATES[self.steps.current]]

    def get_form(self, step=None, data=None, files=None):
        form = super(TrackMilestoneWizard, self).get_form(step, data, files)
        step = step or self.steps.current
        if step == 'My Projects':
            projects = ProjectMilestone.objects.filter(
                project__projectManager=self.request.user,
                project__closed=False,
                closed=False
            ).values('project__id')
            projectsList = list(set([key['project__id'] for key in projects]))
            form.fields['project'].queryset = Project.objects.filter(
                id__in=projectsList
            )
        return form

    def get_form_initial(self, step):
        projectMS = {}
        if step == 'Close Milestone':
            selectedProjectId = self.storage.get_step_data(
                'My Projects'
            )['My Projects-project']
            projectMS = ProjectMilestone.objects.filter(
                project__id=selectedProjectId,
                closed=False
            ).values(
                'id',
                'milestoneDate',
                'description',
                'amount'
            )
        return self.initial_dict.get(step, projectMS)

    def get_context_data(self, form, **kwargs):
        context = super(TrackMilestoneWizard, self).get_context_data(
            form=form, **kwargs)
        if self.steps.current == 'My Projects':
            ms = ProjectMilestone.objects.filter(
                project__projectManager=self.request.user,
                closed=False,
                project__closed=False
            ).values('project').annotate(
                msCount=Count('project')
            ).values('msCount')
            context.update({'msCount': ms})
        return context

    def done(self, form_list, **kwargs):
        updatedData = [form.cleaned_data for form in form_list][1]
        for eachData in updatedData:
            CloseMilestone = ProjectMilestone.objects.get(
                id=eachData['id']
            )
            CloseMilestone.reason = eachData['reason']
            CloseMilestone.amount = eachData['amount']
            CloseMilestone.closed = eachData['closed']
            CloseMilestone.save()
        return HttpResponseRedirect('/myansrsource/dashboard')

TrackMilestone = TrackMilestoneWizard.as_view(TMFORMS)


@login_required
def WrappedTrackMilestoneView(request):
    return TrackMilestone(request)


class ChangeProjectWizard(SessionWizardView):

    def get_template_names(self):
        return [CTEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super(ChangeProjectWizard, self).get_context_data(
            form=form, **kwargs)
        if self.steps.current == 'Change Milestones':
            projectTotal = self.storage.get_step_data(
                'Change Basic Information'
            )['Change Basic Information-revisedTotal']
            context.update({'totalValue': projectTotal})
        if self.steps.current == 'Change Team Members':
            holidays = Holiday.objects.all().values('name', 'date')
            for holiday in holidays:
                holiday['date'] = int(holiday['date'].strftime("%s")) * 1000
            data = {'data': list(holidays)}
            context.update({'holidayList': json.dumps(data)})
        return context

    def get_form(self, step=None, data=None, files=None):
        form = super(ChangeProjectWizard, self).get_form(step, data, files)
        step = step or self.steps.current
        if step == 'My Projects':
            form.fields['project'].queryset = Project.objects.filter(
                projectManager=self.request.user,
                closed=False
            )
        if step == 'Change Basic Information':
            signed = Project.objects.filter(
                id=self.storage.get_step_data(
                    'My Projects'
                )['My Projects-project']).values('signed')[0]
            if signed['signed'] is True:
                form.fields['signed'].widget.attrs[
                    'disabled'
                ] = True

        if step == 'Change Team Members':
            currentProject = ProjectTeamMember.objects.filter(
                project__id=self.storage.get_step_data(
                    'My Projects'
                )['My Projects-project']).values(
                'startDate',
                'endDate',
                )
            for eachData in currentProject:
                startDateDelta = eachData['startDate'] - datetime.now().date()
                endDateDelta = eachData['endDate'] - datetime.now().date()
                if startDateDelta.days <= 0 or endDateDelta.days <= 0:
                    for eachForm in form:
                        eachForm.fields['member'].widget.attrs[
                            'readonly'
                        ] = True
                        eachForm.fields['role'].widget.attrs[
                            'readonly'
                        ] = True
                        eachForm.fields['startDate'].widget.attrs[
                            'readonly'
                        ] = True
                        eachForm.fields['endDate'].widget.attrs[
                            'readonly'
                        ] = True
                        eachForm.fields['rate'].widget.attrs[
                            'readonly'
                        ] = True
                        eachForm.fields['plannedEffort'].widget.attrs[
                            'readonly'
                        ] = True
        if step == 'Change Milestones':
            currentProject = ProjectMilestone.objects.filter(
                project__id=self.storage.get_step_data(
                    'My Projects'
                )['My Projects-project']).values('milestoneDate')
            for eachData in currentProject:
                delta = eachData['milestoneDate'] - datetime.now().date()
                if delta.days <= 0:
                    for eachForm in form:
                        eachForm.fields['milestoneDate'].widget.attrs[
                            'readonly'
                        ] = True
                        eachForm.fields['description'].widget.attrs[
                            'readonly'
                        ] = True
                        eachForm.fields['amount'].widget.attrs[
                            'readonly'
                        ] = True
        return form

    def get_form_initial(self, step):
        currentProject = []
        if step == 'Change Basic Information':
            currentProject = Project.objects.filter(
                id=self.storage.get_step_data(
                    'My Projects'
                )['My Projects-project']).values(
                'id',
                'signed'
                )[0]
        if step == 'Change Team Members':
            currentProject = ProjectTeamMember.objects.filter(
                project__id=self.storage.get_step_data(
                    'My Projects'
                )['My Projects-project']).values(
                'id',
                'member',
                'role',
                'startDate',
                'endDate',
                'plannedEffort',
                'rate'
                )

        if step == 'Change Milestones':
            currentProject = ProjectMilestone.objects.filter(
                project__id=self.storage.get_step_data(
                    'My Projects'
                )['My Projects-project']).values(
                'id',
                'milestoneDate',
                'description',
                'amount',
                )
        return self.initial_dict.get(step, currentProject)

    def done(self, form_list, **kwargs):
        data = UpdateProjectInfo([form.cleaned_data for form in form_list])
        return render(self.request, 'MyANSRSource/changeProjectId.html', data)


def UpdateProjectInfo(newInfo):
    pci = ProjectChangeInfo()
    pci.project = newInfo[0]['project']
    pci.reason = newInfo[1]['reason']
    pci.endDate = newInfo[1]['endDate']
    pci.revisedEffort = newInfo[1]['revisedEffort']
    pci.revisedTotal = newInfo[1]['revisedTotal']
    pci.closed = newInfo[1]['closed']
    if pci.closed is True:
        pci.closedOn = datetime.now()
    pci.signed = newInfo[1]['signed']
    pci.save()

    pcicr = ProjectChangeInfo.objects.get(id=pci.id)
    pcicr.crId = "CR-{0}".format(pci.id)
    pcicr.save()

    prc = Project.objects.get(id=newInfo[1]['id'])
    prc.closed = pci.closed
    prc.signed = pci.signed
    prc.save()

    for eachmember in newInfo[2]:
        if eachmember['id'] == 0:
            ptmc = ProjectTeamMember()
        else:
            ptmc = ProjectTeamMember.objects.get(id=eachmember['id'])
        ptmc.project = pci.project
        ptmc.member = eachmember['member']
        ptmc.role = eachmember['role']
        ptmc.startDate = eachmember['startDate']
        ptmc.endDate = eachmember['endDate']
        ptmc.plannedEffort = eachmember['plannedEffort']
        ptmc.rate = eachmember['rate']
        ptmc.save()

    for eachMilestone in newInfo[3]:
        if eachMilestone['id'] == 0:
            pmc = ProjectMilestone()
        else:
            pmc = ProjectMilestone.objects.get(id=eachMilestone['id'])
        pmc.project = pci.project
        pmc.milestoneDate = eachMilestone['milestoneDate']
        pmc.description = eachMilestone['description']
        pmc.save()

    return {'crId': pcicr.crId}

changeProject = ChangeProjectWizard.as_view(CFORMS)


@login_required
def WrappedChangeProjectView(request):
    return changeProject(request)


class CreateProjectWizard(SessionWizardView):

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_form(self, step=None, data=None, files=None):
        form = super(CreateProjectWizard, self).get_form(step, data, files)
        step = step or self.steps.current
        if step == 'Define Project':
            if form.is_valid():
                self.request.session['PStartDate'] = form.cleaned_data[
                    'startDate'
                ].strftime('%Y-%m-%d')
                self.request.session['PEndDate'] = form.cleaned_data[
                    'endDate'
                ].strftime('%Y-%m-%d')

        if step == 'Define Team':
            for eachForm in form:
                eachForm.fields['DELETE'].widget.attrs[
                    'disabled'
                ] = True
            if form.is_valid():
                if eachForm.cleaned_data['rate'] > 100:
                    rate = eachForm.cleaned_data['rate']
                    errors = eachForm._errors.setdefault(rate, ErrorList())
                    errors.append(u'% value cannot be greater than 100')

        if step == 'Financial Milestones':
            internalStatus = self.storage.get_step_data('Basic Information')[
                'Basic Information-internal'
            ]
            for eachForm in form:
                eachForm.fields['DELETE'].widget.attrs[
                    'disabled'
                ] = True
            if internalStatus == 'True':
                for eachForm in form:
                    eachForm.fields['milestoneDate'].widget.attrs[
                        'readonly'
                    ] = True
                    eachForm.fields['description'].widget.attrs[
                        'readonly'
                    ] = True
                    eachForm.fields['description'].widget.attrs[
                        'value'
                    ] = None
                    eachForm.fields['amount'].widget.attrs[
                        'readonly'
                    ] = True
                    eachForm.fields['DELETE'].widget.attrs[
                        'readonly'
                    ] = True
            else:
                if form.is_valid():
                    projectTotal = self.storage.get_step_data('Define Project')[
                        'Define Project-totalValue'
                    ]
                    totalRate = 0
                    for t in form.cleaned_data:
                        totalRate += t['amount']
                    for eachForm in form:
                        if int(projectTotal) != totalRate:
                            errors = eachForm._errors.setdefault(
                                totalRate,
                                ErrorList())
                            errors.append(u'Total amount must be \
                                            equal to project value')
        return form

    def get_context_data(self, form, **kwargs):
        context = super(CreateProjectWizard, self).get_context_data(
            form=form, **kwargs)
        if self.steps.current == 'Financial Milestones':
            projectTotal = self.storage.get_step_data('Define Project')[
                'Define Project-totalValue'
            ]
            context.update({'totalValue': projectTotal})
        if self.steps.current == 'Define Team':
            holidays = Holiday.objects.all().values('name', 'date')
            for holiday in holidays:
                holiday['date'] = int(holiday['date'].strftime("%s")) * 1000
            data = {'data': list(holidays)}
            context.update({'holidayList': json.dumps(data)})
        return context

    def get_form_initial(self, step):
        initValue = {}
        if step == 'Define Team':
            initValue = [{'startDate': self.request.session['PStartDate'],
                          'endDate': self.request.session['PEndDate']},
                         {'startDate': self.request.session['PStartDate'],
                          'endDate': self.request.session['PEndDate']}]
        return self.initial_dict.get(step, initValue)

    def done(self, form_list, **kwargs):
        teamDataCounter = 0
        milestoneDataCounter = 0
        changedTeamData = {}
        changedMilestoneData = {}
        cleanedTeamData = []
        cleanedMilestoneData = []

        basicInfo = [form.cleaned_data for form in form_list][0]
        if basicInfo['plannedEffort'] > 0:
            revenueRec = basicInfo['totalValue'] / basicInfo['plannedEffort']
        else:
            revenueRec = 0
        chapterList = []
        for eachChapter in basicInfo['chapters']:
            chapterList.append(eachChapter.id)
        self.request.session['chapters'] = chapterList
        self.request.session['bu'] = basicInfo['bu'].id
        self.request.session['book'] = basicInfo['book'].id
        self.request.session['customer'] = basicInfo['customer'].id
        basicInfo['startDate'] = basicInfo.get(
            'startDate'
        ).strftime('%Y-%m-%d')
        basicInfo['endDate'] = basicInfo.get(
            'endDate'
        ).strftime('%Y-%m-%d')
        flagData = {}
        for k, v in [form.cleaned_data for form in form_list][1].iteritems():
            flagData[k] = v
        effortTotal = 0
        for teamData in [form.cleaned_data for form in form_list][2]:
            teamDataCounter += 1
            for k, v in teamData.iteritems():
                if k == 'plannedEffort':
                    effortTotal += v
                k = "{0}-{1}".format(k, teamDataCounter)
                changedTeamData[k] = v
                if 'role' in k:
                    self.request.session[k] = v.id
            startDate = 'startDate-{0}'.format(teamDataCounter)
            changedTeamData[startDate] = changedTeamData.get(
                startDate
            ).strftime('%Y-%m-%d')
            endDate = 'endDate-{0}'.format(teamDataCounter)
            changedTeamData[endDate] = changedTeamData.get(
                endDate
            ).strftime('%Y-%m-%d')
            teamMemberId = 'teamMemberId-{0}'.format(teamDataCounter)
            member = 'member-{0}'.format(teamDataCounter)
            changedTeamData[teamMemberId] = changedTeamData.get(member).id
            DELETE = 'DELETE-{0}'.format(teamDataCounter)
            del changedTeamData[DELETE]
            self.request.session['totalMemberCount'] = teamDataCounter + 1
            cleanedTeamData.append(changedTeamData.copy())
            changedTeamData.clear()

        if [form.cleaned_data for form in form_list][1]['internal'] is False:
            for milestoneData in [form.cleaned_data for form in form_list][3]:
                milestoneDataCounter += 1
                for k, v in milestoneData.iteritems():
                    k = "{0}-{1}".format(k, milestoneDataCounter)
                    changedMilestoneData[k] = v
                milestoneDate = 'milestoneDate-{0}'.format(milestoneDataCounter)
                changedMilestoneData[milestoneDate] = changedMilestoneData.get(
                    milestoneDate
                ).strftime('%Y-%m-%d')
                DELETE = 'DELETE-{0}'.format(milestoneDataCounter)
                del changedMilestoneData[DELETE]
                self.request.session[
                    'totalMilestoneCount'
                ] = milestoneDataCounter + 1
                cleanedMilestoneData.append(changedMilestoneData.copy())
                changedMilestoneData.clear()
        if [form.cleaned_data for form in form_list][1]['internal'] is True:
            data = {
                'basicInfo': basicInfo,
                'flagData': flagData,
                'effortTotal': effortTotal,
                'revenueRec': revenueRec,
                'teamMember': cleanedTeamData,
            }
        else:
            data = {
                'basicInfo': basicInfo,
                'flagData': flagData,
                'effortTotal': effortTotal,
                'revenueRec': revenueRec,
                'teamMember': cleanedTeamData,
                'milestone': cleanedMilestoneData
            }
        return render(self.request, 'MyANSRSource/projectSnapshot.html', data)


@login_required
def saveProject(request):
    if request.method == 'POST':
        pr = Project()
        pr.name = request.POST.get('name')
        pr.projectType = request.POST.get('projectType')
        projectname = request.POST.get('name')
        projectname = projectname.replace(' ', '_').lower()
        projectname = re.sub('[^a-z_]+', '', projectname)
        if projectname.endswith('_'):
            projectname = projectname[:-1]
        minWordCount = len(min(projectname.split('_'), key=len))
        strippedWord = [e[:minWordCount] for e in projectname.split('_')]
        projectname = '_'.join(strippedWord)
        pnLength = len(projectname)
        while (pnLength > 15):
            strippedWord = [
                e[:-1]
                for e in projectname.split('_')
            ]
            pnLength = len('_'.join(strippedWord))
            projectname = '_'.join(strippedWord)
        projectName = projectname
        pr.startDate = request.POST.get('startDate')
        pr.endDate = request.POST.get('endDate')
        pr.plannedEffort = request.POST.get('plannedEffort')
        pr.currentProject = request.POST.get('currentProject')
        if request.POST.get('signed') == 'False':
            signed = False
        else:
            signed = True
        pr.signed = signed
        if request.POST.get('internal') == 'False':
            internalValue = False
        else:
            internalValue = True
        pr.internal = internalValue
        pr.contingencyEffort = request.POST.get('contingencyEffort')
        pr.projectManager = request.user
        pr.bu = CompanyMaster.models.BusinessUnit.objects.filter(
            id=request.session['bu']
        )[0]
        pr.customer = CompanyMaster.models.Customer.objects.filter(
            id=request.session['customer']
        )[0]
        pr.book = Book.objects.filter(id=request.session['book'])[0]
        pr.save()
        request.session['currentProject'] = pr.id
        request.session['currentProjectName'] = pr.name

        projectIdPrefix = "{0}_{1}_{2}_".format(
            request.POST.get('projectType'),
            datetime.now().year,
            str(pr.id).zfill(4)
        )
        pru = Project.objects.get(id=pr.id)
        pru.projectId = "{0}{1}".format(projectIdPrefix, projectName)
        print pru.projectId
        pru.save()
        request.session['currentProjectId'] = pru.projectId

        for eachId in request.session['chapters']:
            pr.chapters.add(eachId)

        for memberCount in range(1, request.session['totalMemberCount']):
            ptm = ProjectTeamMember()
            ptm.project = pr
            teamMemberId = "teamMemberId-{0}".format(memberCount)
            role = "role-{0}".format(memberCount)
            plannedEffort = "plannedEffort-{0}".format(memberCount)
            rate = "rate-{0}".format(memberCount)
            startDate = "startDate-{0}".format(memberCount)
            endDate = "endDate-{0}".format(memberCount)

            ptm.member = User.objects.get(
                pk=request.POST.get(teamMemberId)
            )
            ptm.role = employee.models.Designation.objects.filter(
                pk=request.session[role]
            )[0]
            ptm.plannedEffort = request.POST.get(plannedEffort)
            ptm.rate = request.POST.get(rate)
            ptm.startDate = request.POST.get(startDate)
            ptm.endDate = request.POST.get(endDate)
            ptm.save()

        if internalValue is False:
            for milestoneCount in range(1, request.session[
                'totalMilestoneCount'
            ]):
                pms = ProjectMilestone()
                pms.project = pr
                milestoneDate = 'milestoneDate-{0}'.format(milestoneCount)
                description = 'description-{0}'.format(milestoneCount)
                amount = 'amount-{0}'.format(milestoneCount)
                pms.milestoneDate = request.POST.get(milestoneDate)
                pms.description = request.POST.get(description)
                pms.amount = request.POST.get(amount)
                pms.save()

        data = {'projectId': pru.projectId, 'projectName': pr.name}
        return render(request, 'MyANSRSource/projectSuccess.html', data)

createProject = CreateProjectWizard.as_view(FORMS)


@login_required
def WrappedCreateProjectView(request):
    return createProject(request)


@login_required
def notify(request):
    projectId = request.session['currentProject']
    projectHead = CompanyMaster.models.Customer.objects.filter(
        id=request.session['customer'],
    ).values('relatedMember__email',
             'relatedMember__first_name',
             'relatedMember__last_name')
    for eachHead in projectHead:
        if eachHead['relatedMember__email'] != '':
            notifyTeam = EmailMultiAlternatives('Congrats!!!',
                                                'hai',
                                                settings.EMAIL_HOST_USER,
                                                ['{0}'.format(
                                                    eachHead[
                                                        'relatedMember__email'
                                                    ]
                                                )],)

            emailTemp = render_to_string(
                'projectCreatedHeadEmail.html',
                {
                    'firstName': eachHead['relatedMember__first_name'],
                    'lastName': eachHead['relatedMember__last_name'],
                    'projectId': projectId
                }
            )
            notifyTeam.attach_alternative(emailTemp, 'text/html')
            notifyTeam.send()
    projectId = request.session['currentProject']
    teamMembers = ProjectTeamMember.objects.filter(
        project=projectId
    ).values('member__email', 'member__first_name', 'member__last_name')
    for eachMember in teamMembers:
        if eachMember['member__email'] != '':
            notifyTeam = EmailMultiAlternatives('Congrats!!!',
                                                'hai',
                                                settings.EMAIL_HOST_USER,
                                                ['{0}'.format(
                                                    eachMember['member__email']
                                                )],)

            emailTemp = render_to_string(
                'projectCreatedEmail.html',
                {
                    'firstName': eachMember['member__first_name'],
                    'lastName': eachMember['member__last_name'],
                    'projectId': projectId
                }
            )
            notifyTeam.attach_alternative(emailTemp, 'text/html')
            notifyTeam.send()
    projectName = request.session['currentProjectName']
    data = {'projectId': request.session['currentProjectId'],
            'projectName': projectName,
            'notify': 'F'}
    return render(request, 'MyANSRSource/projectSuccess.html', data)


@login_required
def deleteProject(request):
    ProjectBasicInfoForm()
    ProjectTeamForm()
    ProjectMilestoneForm()
    return HttpResponseRedirect('add')


def GetChapters(request, bookid):
    chapters = Chapter.objects.filter(book__id=bookid)
    json_chapters = serializers.serialize("json", chapters)
    return HttpResponse(json_chapters, content_type="application/javascript")


def GetProjectType(request):
    typeData = ProjectTeamMember.objects.values(
        'project__id',
        'project__name',
        'project__projectType'
    ).filter(project__closed=False,
             member=request.user
             )
    data = {'data': list(typeData)}
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type="application/json")


def Logout(request):
    logout(request)
    request.session.flush()
    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
    return HttpResponseRedirect('/myansrsource')
