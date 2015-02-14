import logging
import json

from django.forms.util import ErrorList
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.contrib import auth, messages
from django.shortcuts import render
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.formtools.wizard.views import SessionWizardView
from django.forms.formsets import formset_factory
from datetime import datetime, timedelta
from django.db.models import Q
from django.conf import settings

from templated_email import send_templated_mail

from MyANSRSource.models import Project, TimeSheetEntry, \
    ProjectMilestone, ProjectTeamMember, Book, ProjectChangeInfo, \
    Chapter, projectType

from MyANSRSource.forms import LoginForm, ProjectBasicInfoForm, \
    ProjectTeamForm, ProjectMilestoneForm, \
    ActivityForm, TimesheetFormset, ProjectFlagForm, \
    ChangeProjectBasicInfoForm, ChangeProjectTeamMemberForm, \
    ChangeProjectMilestoneForm, ChangeProjectForm, \
    CloseProjectMilestoneForm

import CompanyMaster
from CompanyMaster.models import Holiday
import employee


from ldap import LDAPError
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
        extra=1,
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
        can_delete=True
    )),
    ("Change Milestones", formset_factory(
        ChangeProjectMilestoneForm,
        extra=0,
        can_delete=True
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
    if request.user.is_authenticated():
        return HttpResponseRedirect('/myansrsource/dashboard')
    elif request.method == 'POST':
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
    # Week Calculation.
    leaveDayWork = False
    # Getting the form values and storing it to DB.
    tsStatus = {}
    if request.method == 'POST':
        # Getting the forms with submitted values
        tsform = TimesheetFormset(request.user)
        tsFormset = formset_factory(
            tsform, extra=1, can_delete=True
        )
        atFormset = formset_factory(
            ActivityForm, extra=1, can_delete=True
        )
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
            mondayTotal = 0.0
            tuesdayTotal = 0.0
            wednesdayTotal = 0.0
            thursdayTotal = 0.0
            fridayTotal = 0.0
            saturdayTotal = 0.0
            sundayTotal = 0.0
            weekTotal = 0.0
            billableTotal = 0.0
            nonbillableTotal = 0.0
            weekHolidays = []
            (timesheetList, activitiesList,
             timesheetDict, activityDict) = ([], [], {}, {})
            if hasattr(request.user, 'employee'):
                locationId = request.user.employee.location
                weekHolidays = Holiday.objects.filter(
                    location=locationId,
                    date__range=[changedStartDate, changedEndDate]
                ).values('date')
            else:
                weekHolidays = []
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
                            mondayTotal += float(v)
                        elif k == 'tuesdayH':
                            tuesdayTotal += float(v)
                        elif k == 'wednesdayH':
                            wednesdayTotal += float(v)
                        elif k == 'thursdayH':
                            thursdayTotal += float(v)
                        elif k == 'fridayH':
                            fridayTotal += float(v)
                        elif k == 'saturdayH':
                            saturdayTotal += float(v)
                        elif k == 'sundayH':
                            sundayTotal += float(v)
                        elif k == 'totalH':
                            billableTotal += float(v)
                            weekTotal += float(v)
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
                            mondayTotal += float(v)
                        elif k == 'activity_tuesday':
                            tuesdayTotal += float(v)
                        elif k == 'activity_wednesday':
                            wednesdayTotal += float(v)
                        elif k == 'activity_thursday':
                            thursdayTotal += float(v)
                        elif k == 'activity_friday':
                            fridayTotal += float(v)
                        elif k == 'activity_saturday':
                            saturdayTotal += float(v)
                        elif k == 'activity_sunday':
                            sundayTotal += float(v)
                        elif k == 'total':
                            nonbillableTotal += float(v)
                            weekTotal += float(v)
                        activityDict[k] = v
                    activitiesList.append(activityDict.copy())
                    activityDict.clear()
            if (mondayTotal > 24) | (tuesdayTotal > 24) | \
                    (wednesdayTotal > 24) | (thursdayTotal > 24) | \
                    (fridayTotal > 24) | (saturdayTotal > 24) | \
                    (sundayTotal > 24):
                messages.error(request, 'You can only work for 24 hours a day')
            elif (weekTotal < 36) | (weekTotal > 44) | \
                 (billableTotal > 44) | (nonbillableTotal > 40) | \
                 (leaveDayWork is True):
                for eachActivity in activitiesList:
                    # Getting objects for models
                    if eachActivity['atId'] > 0:
                        nonbillableTS = TimeSheetEntry.objects.get(
                            pk=eachActivity['atId']
                        )
                    else:
                        nonbillableTS = TimeSheetEntry()
                    # Common values for Billable and Non-Billable
                    nonbillableTS.wkstart = changedStartDate
                    nonbillableTS.wkend = changedEndDate
                    nonbillableTS.teamMember = request.user
                    if 'save' not in request.POST:
                        nonbillableTS.hold = True
                    if (weekTotal < 36) | (weekTotal > 44):
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
                    eachActivity['atId'] = nonbillableTS.id
                tsStatus = []
                for eachTimesheet in timesheetList:
                    statusD = {}
                    if eachTimesheet['tsId'] > 0:
                        billableTS = TimeSheetEntry.objects.filter(
                            id=eachTimesheet['tsId']
                        )[0]
                    else:
                        billableTS = TimeSheetEntry()
                    billableTS.wkstart = changedStartDate
                    billableTS.wkend = changedEndDate
                    billableTS.teamMember = request.user
                    if 'save' not in request.POST:
                        billableTS.hold = True
                    billableTS.billable = True
                    if (weekTotal < 36) | (weekTotal > 44):
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
                    eachTimesheet['tsId'] = billableTS.id
                    statusD['toApprove'] = True
                    statusD['id'] = int(billableTS.project.id)
                    tsStatus.append(statusD)
                if 'save' not in request.POST:
                    messages.warning(
                        request,
                        'Your timesheet has been sent to your \
                        manager for approval')
                    hold = True
            elif 'save' not in request.POST:
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
                    nonbillableTS.managerFeedback = 'System Approved'
                    nonbillableTS.hold = True
                    nonbillableTS.approvedon = datetime.now()
                    for k, v in eachActivity.iteritems():
                        setattr(nonbillableTS, k, v)
                    nonbillableTS.save()
                    eachActivity['atId'] = nonbillableTS.id
                tsStatus = []
                for eachTimesheet in timesheetList:
                    statusD = {}
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
                    billableTS.managerFeedback = 'System Approved'
                    billableTS.approved = True
                    billableTS.approvedon = datetime.now()
                    billableTS.hold = True
                    for k, v in eachTimesheet.iteritems():
                        setattr(billableTS, k, v)
                    billableTS.save()
                    eachTimesheet['tsId'] = billableTS.id
                    statusD['approved'] = True
                    statusD['id'] = int(billableTS.project.id)
                    tsStatus.append(statusD)
                    hold = False
                messages.success(request, 'Your timesheet has been approved')
            dates = switchWeeks(request)
            if 'save' in request.POST:
                msg = 'Your timesheet has been saved. You can continue to \
                    make changes. Please submit your timesheet once \
                    you have completed it'
                messages.success(request, msg)
                hold = False
            tsContent = timesheetList
            atContent = activitiesList
            tsErrorList = []
        else:
            # Switch dates back and forth
            dates = switchWeeks(request)
            tsErrorList = timesheets.errors
            tsContent = [k.cleaned_data for k in timesheets]
            for eachErrorData in tsContent:
                for k, v in eachErrorData.iteritems():
                    if k == 'project':
                        ptype = Project.objects.filter(
                            id=eachErrorData['project'].id
                        ).values('projectType__code')[0]['projectType__code']
                        eachErrorData['projectType'] = ptype
            atContent = [k for k in activities.cleaned_data]
            hold = False
        data = {'weekstartDate': dates['start'],
                'weekendDate': dates['end'],
                'disabled': dates['disabled'],
                'hold': hold,
                'extra': 0,
                'ErrorList': tsErrorList,
                'tsFormList': tsContent,
                'atFormList': atContent,
                'tsId': billableTS.id,
                'atId': nonbillableTS.id}
        return renderTimesheet(request, data)
    else:
        # Switch dates back and forth
        dates = switchWeeks(request)

        # Getting Data for timesheet and activity
        unApprovedData = getUnapprovedDataList(request, dates['start'],
                                               dates['end'])
        approvedData = getApprovedDataList(request, dates['start'],
                                           dates['end'])

        # Common values initialization
        extra = 0
        hold = False

        # Approved TS data
        if len(approvedData['tsData']):
            tsStatus['approved'] = True
            tsFormList = approvedData['tsData']
            atFormList = approvedData['atData']
            messages.success(request, 'Timesheet is approved for this week')

        # To be approved TS data
        elif len(unApprovedData['tsData']):
            hold = unApprovedData['tsData'][0]['hold']
            tsFormList = unApprovedData['tsData']
            atFormList = unApprovedData['atData']
            if hold:
                messages.warning(request, 'Your timesheet is currently \
                                 pending with your manager for review')
            else:
                messages.warning(request, 'Please update your timesheet')

        # Fresh TS data
        else:
            tsFormList, atFormList = [], []
            extra = 1
            messages.success(request, 'Please enter your timesheet \
                             for this week')

        data = {'weekstartDate': dates['start'],
                'weekendDate': dates['end'],
                'disabled': dates['disabled'],
                'hold': hold,
                'extra': extra,
                'tsFormList': tsFormList,
                'atFormList': atFormList}
        return renderTimesheet(request, data)


@login_required
def switchWeeks(request):
    today = datetime.now().date()
    weekstartDate = today - timedelta(days=datetime.now().date().weekday())
    ansrEndDate = weekstartDate + timedelta(days=6)
    disabled = 'next'
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
    return {'start': weekstartDate, 'end': ansrEndDate, 'disabled': disabled}


@login_required
def getUnapprovedDataList(request, weekstartDate, ansrEndDate):
    # To be approved TS data
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
             'managerFeedback', 'approved', 'hold'
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
             'saturdayH', 'saturdayQ', 'sundayH', 'sundayQ', 'approved',
             'totalH', 'totalQ', 'managerFeedback', 'project__projectType__code'
             )

    # Changing data TS data
    tsData = {}
    tsDataList = []
    for eachData in cwTimesheetData:
        for k, v in eachData.iteritems():
            tsData[k] = v
            if k == 'managerFeedback':
                tsData['feedback'] = v
            if k == 'id':
                tsData['tsId'] = v
            if k == 'project__projectType__code':
                tsData['projectType'] = v
        tsDataList.append(tsData.copy())
        tsData.clear()
    atData = {}
    atDataList = []
    for eachData in cwActivityData:
        for k, v in eachData.iteritems():
            if k == 'activity':
                atData['activity'] = v
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
    return {'tsData': tsDataList, 'atData': atDataList}


@login_required
def getApprovedDataList(request, weekstartDate, ansrEndDate):
    # Approved TS Data
    cwApprovedActivityData = TimeSheetEntry.objects.filter(
        Q(
            wkstart=weekstartDate,
            wkend=ansrEndDate,
            teamMember=request.user,
            approved=True,
            project__isnull=True
        )
    ).values('activity', 'mondayH', 'tuesdayH', 'wednesdayH', 'thursdayH',
             'fridayH', 'saturdayH', 'sundayH', 'totalH', 'managerFeedback',
             'approved', 'hold'
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
             'tuesdayH', 'wednesdayH', 'thursdayH', 'task', 'id',
             'fridayH', 'saturdayH', 'sundayH', 'totalH', 'managerFeedback',
             'approved', 'hold'
             )
    return {'tsData': cwApprovedTimesheetData, 'atData': cwApprovedActivityData}


@login_required
def renderTimesheet(request, data):
    billableHours = TimeSheetEntry.objects.filter(
        Q(
            wkstart=data['weekstartDate'],
            wkend=data['weekendDate'],
            teamMember=request.user,
            approved=False,
            activity__isnull=True
        ),
        ~Q(task='I')
    ).values('totalH')
    idleHours = TimeSheetEntry.objects.filter(
        Q(
            wkstart=data['weekstartDate'],
            wkend=data['weekendDate'],
            task='I',
            teamMember=request.user,
            approved=False,
            activity__isnull=True
        ),
    ).values('totalH')
    othersHours = TimeSheetEntry.objects.filter(
        Q(
            wkstart=data['weekstartDate'],
            wkend=data['weekendDate'],
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
    tsform = TimesheetFormset(request.user)
    tsFormset = formset_factory(tsform,
                                extra=data['extra'],
                                can_delete=True)
    atFormset = formset_factory(ActivityForm,
                                extra=data['extra'],
                                can_delete=True)
    if len(data['tsFormList']):
        atFormset = atFormset(initial=data['atFormList'], prefix='at')
        tsFormset = tsFormset(initial=data['tsFormList'])
    else:
        atFormset = atFormset(prefix='at')
    finalData = {'weekstartDate': data['weekstartDate'],
                 'weekendDate': data['weekendDate'],
                 'disabled': data['disabled'],
                 'hold': data['hold'],
                 'shortDays': ['Mon', 'Tue', 'Wed', 'Thu',
                               'Fri', 'Sat', 'Sun'],
                 'billableHours': billableHours,
                 'idleHours': idleHours,
                 'bTotal': bTotal,
                 'idleTotal': idleTotal,
                 'othersTotal': othersTotal,
                 'tsFormset': tsFormset,
                 'atFormset': atFormset}
    if 'tsErrorList' in data:
        finalData['tsErrorList'] = data['tsErrorList']
    return render(request, 'MyANSRSource/timesheetEntry.html', finalData)


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
            approved=False, hold=True
        ).values('id', 'project__id', 'project__name', 'wkstart', 'wkend',
                 'teamMember__username', 'totalH', 'exception', 'approved',
                 'managerFeedback').order_by('project__id')

        data = {
            'timesheetInfo': unApprovedTimeSheet
        }
        return render(request, 'MyANSRSource/timesheetApprove.html', data)


@login_required
def Dashboard(request):
    totalActiveProjects = Project.objects.filter(
        projectManager=request.user,
        closed=False
    ).count() if request.user.has_perm('MyANSRSource.manage_project') else 0

    unApprovedTimeSheet = TimeSheetEntry.objects.filter(
        project__projectManager=request.user,
        approved=False, hold=True
    ).count() if request.user.has_perm('MyANSRSource.approve_timesheet') else 0

    totalEmployees = User.objects.all().count()
    activeMilestones = ProjectMilestone.objects.filter(
        project__projectManager=request.user,
        project__closed=False,
        closed=False
    ).count() if request.user.has_perm('MyANSRSource.manage_milestones') else 0

    tsProjectsCount = ProjectTeamMember.objects.filter(
        project__closed=False,
        member=request.user
    ).values('project__id').annotate(dcount=Count('project__id'))

    TSProjectsCount = len(tsProjectsCount)

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
    trainings = CompanyMaster.models.Training.objects.all().values(
        'batch', 'trainingDate')
    if len(trainings):
        for eachTraining in trainings:
            eachTraining['trainingDate'] = eachTraining[
                'trainingDate'
            ].strftime('%Y-%m-%d')
    else:
        trainings = []
    if hasattr(request.user, 'employee'):
        locationId = request.user.employee.location
        holidayList = Holiday.objects.filter(
            location=locationId
        ).values('name', 'date')
        for eachHoliday in holidayList:
            eachHoliday['date'] = eachHoliday['date'].strftime('%Y-%m-%d')
    else:
        holidayList = []
    data = {
        'username': request.user.username,
        'firstname': request.user.first_name,
        'TSProjectsCount': TSProjectsCount,
        'holidayList': holidayList,
        'projectsList': myprojects,
        'trainingList': trainings,
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
    try:
        user = authenticate(username=userName, password=password)
        if user is not None:
            if user.is_active:
                if user.has_perm('MyANSRSource.enter_timesheet'):
                    auth.login(request, user)
                    return HttpResponseRedirect('/myansrsource/dashboard')
                else:
                    # We have an unknow group
                    messages.error(
                        request,
                        'This user does not have access to timesheets.')
                    logging.error('User {0} permission details {1}'.format(
                        user.username,
                        user.get_all_permissions()))
                    return loginResponse(
                        request,
                        form,
                        'MyANSRSource/index.html')
            else:
                messages.error(request, 'Sorry this user is not active.')
                return loginResponse(request, form, 'MyANSRSource/index.html')
        else:
            messages.error(
                request,
                'Invalid userid & password / User could not be found \
                on Active Directory.')
            return loginResponse(request, form, 'MyANSRSource/index.html')
    except LDAPError as e:
        messages.error(
            request,
            'This user has LDAP setup issue:' + str(e))
        return loginResponse(request, form, 'MyANSRSource/index.html')
    except:
        messages.error(
            request,
            'Unknown Active directory error occured.\
            Please check your userid/password.  Do not use ANSR prefix \
            in your username.')
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
            if hasattr(self.request.user, 'employee'):
                locationId = self.request.user.employee.location
                holidays = Holiday.objects.filter(
                    location=locationId
                ).values('name', 'date')
                holidays = Holiday.objects.all().values('name', 'date')
                for holiday in holidays:
                    holiday['date'] = int(
                        holiday['date'].strftime("%s")) * 1000
                data = {'data': list(holidays)}
            else:
                data = {'data': ''}
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
                    'readonly'
                ] = 'True'
            if form.is_valid():
                if form.has_changed():
                    self.request.session['changed'] = True
                else:
                    self.request.session['changed'] = False

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
                        ] = 'True'
                        eachForm.fields['role'].widget.attrs[
                            'readonly'
                        ] = 'True'
                        eachForm.fields['startDate'].widget.attrs[
                            'readonly'
                        ] = 'True'
                        eachForm.fields['endDate'].widget.attrs[
                            'readonly'
                        ] = 'True'
                        eachForm.fields['rate'].widget.attrs[
                            'readonly'
                        ] = 'True'
                        eachForm.fields['plannedEffort'].widget.attrs[
                            'readonly'
                        ] = 'True'
                        eachForm.fields['DELETE'].widget.attrs[
                            'readonly'
                        ] = 'True'
                        eachForm.fields['DELETE'].widget.attrs[
                            'class'
                        ] = 'form-control'
            if self.request.session['changed'] is False:
                if form.is_valid():
                    if form.has_changed():
                        self.request.session['changed'] = True
                    else:
                        self.request.session['changed'] = False
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
                        ] = 'True'
                        eachForm.fields['description'].widget.attrs[
                            'readonly'
                        ] = 'True'
                        eachForm.fields['amount'].widget.attrs[
                            'readonly'
                        ] = 'True'
                        eachForm.fields['financial'].widget.attrs[
                            'readonly'
                        ] = 'True'
                        eachForm.fields['DELETE'].widget.attrs[
                            'readonly'
                        ] = 'True'
                        eachForm.fields['DELETE'].widget.attrs[
                            'class'
                        ] = 'form-control'
                for eachForm in form:
                    if eachForm.is_valid():
                        if eachForm.cleaned_data['financial'] is False:
                            if eachForm.cleaned_data['amount'] > 0:
                                amount = form.cleaned_data[0]['amount']
                                errors = eachForm._errors.setdefault(
                                    amount,
                                    ErrorList())
                                errors.append(u'Please select milestone as \
                                                financial')
                        elif eachForm.cleaned_data['amount'] == 0:
                            amount = form.cleaned_data[0]['amount']
                            errors = eachForm._errors.setdefault(
                                amount,
                                ErrorList())
                            errors.append(u'Financial Milestone amount \
                                        cannot be 0')
            if self.request.session['changed'] is False:
                if form.is_valid():
                    if form.has_changed():
                        self.request.session['changed'] = True
                    else:
                        self.request.session['changed'] = False
        return form

    def get_form_initial(self, step):
        currentProject = []
        if step == 'Change Basic Information':
            currentProject = Project.objects.filter(
                id=self.storage.get_step_data(
                    'My Projects'
                )['My Projects-project']).values(
                'id',
                'signed',
                'endDate',
                'plannedEffort',
                'totalValue'
                )[0]
            currentProject['revisedTotal'] = currentProject['totalValue']
            currentProject['revisedEffort'] = currentProject['plannedEffort']
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
                'financial'
                )
        return self.initial_dict.get(step, currentProject)

    def done(self, form_list, **kwargs):
        if self.request.session['changed'] is True:
            data = UpdateProjectInfo(
                self.request, [
                    form.cleaned_data for form in form_list])
            return render(
                self.request,
                'MyANSRSource/changeProjectId.html',
                data)
        else:
            return render(
                self.request,
                'MyANSRSource/NochangeProject.html',
                {})


def UpdateProjectInfo(request, newInfo):
    """
        newInfo[0] ==> Selected Project Object
        newInfo[1] ==> 'reason' , 'endDate', 'revisedEffort', 'revisedTotal',
                       'closed', 'signed'
        newInfo[2] ==> TeamMembers object(Old Data + Newly added member if any)
        newInfo[3] ==> Milesonte Object(old Data + Newly add milestones if any)
    """
    try:
        prc = newInfo[0]['project']
        prc.closed = newInfo[1]['closed']
        print newInfo[1]['signed']
        prc.signed = newInfo[1]['signed']
        prc.save()

        pci = ProjectChangeInfo()
        pci.project = prc
        pci.reason = newInfo[1]['reason']
        pci.endDate = newInfo[1]['endDate']
        pci.revisedEffort = newInfo[1]['revisedEffort']
        pci.revisedTotal = newInfo[1]['revisedTotal']
        pci.closed = newInfo[1]['closed']
        if pci.closed is True:
            pci.closedOn = datetime.now()
        pci.signed = newInfo[1]['signed']
        pci.save()

        # We need the Primary key to create the CRId
        pci.crId = "CR-{0}".format(pci.id)
        pci.save()

        for eachmember in newInfo[2]:
            if eachmember['id'] == 0:
                ptmc = ProjectTeamMember()
            else:
                ptmc = ProjectTeamMember.objects.get(id=eachmember['id'])
            ptmc.project = prc
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
            pmc.project = prc
            pmc.milestoneDate = eachMilestone['milestoneDate']
            pmc.description = eachMilestone['description']
            pmc.amount = eachMilestone['amount']
            pmc.financial = eachMilestone['financial']
            pmc.save()

        return {'crId': pci.crId}
    except (ProjectTeamMember.DoesNotExist,
            ProjectMilestone.DoesNotExist) as e:
        messages.error(request, 'Could not save change request information')
        logging.error('Exception in UpdateProjectInfo :' + str(e))
        return {'crId': None}

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
            c = {}
            for eachForm in form:
                if int(eachForm.prefix.split('-')[1]) < 2:
                    eachForm.fields['DELETE'].widget.attrs[
                        'disabled'
                    ] = 'True'
                if eachForm.is_valid():
                    c.setdefault(eachForm.cleaned_data['member'], []
                                 ).append(eachForm.cleaned_data['rate'])
                    if eachForm.cleaned_data['rate'] > 100:
                        rate = eachForm.cleaned_data['rate']
                        errors = eachForm._errors.setdefault(rate, ErrorList())
                        errors.append(u'% value cannot be greater than 100')
                    for k, v in c.iteritems():
                        if sum(tuple(v)) > 100:
                            errors = eachForm._errors.setdefault(
                                sum(tuple(v)), ErrorList())
                            errors.append(
                                u'No person can have more than 100% as effort')

        if step == 'Financial Milestones':
            internalStatus = self.storage.get_step_data('Basic Information')[
                'Basic Information-internal'
            ]
            for eachForm in form:
                eachForm.fields['DELETE'].widget.attrs[
                    'disabled'
                ] = 'True'
            if internalStatus == 'True':
                for eachForm in form:
                    eachForm.fields['milestoneDate'].widget.attrs[
                        'readonly'
                    ] = 'True'
                    eachForm.fields['description'].widget.attrs[
                        'readonly'
                    ] = 'True'
                    eachForm.fields['description'].widget.attrs[
                        'value'
                    ] = None
                    eachForm.fields['amount'].widget.attrs[
                        'readonly'
                    ] = 'True'
                    eachForm.fields['DELETE'].widget.attrs[
                        'readonly'
                    ] = 'True'
            else:
                if form.is_valid():
                    projectTotal = self.storage.get_step_data('Define Project')[
                        'Define Project-totalValue'
                    ]
                    totalRate = 0
                    for eachForm in form:
                        if eachForm.is_valid():
                            totalRate += eachForm.cleaned_data['amount']
                            if eachForm.cleaned_data['financial'] is False:
                                if eachForm.cleaned_data['amount'] > 0:
                                    amount = form.cleaned_data[0]['amount']
                                    errors = eachForm._errors.setdefault(
                                        amount,
                                        ErrorList())
                                    errors.append(u'Please select milestone as \
                                                  financial')
                            elif eachForm.cleaned_data['amount'] == 0:
                                amount = form.cleaned_data[0]['amount']
                                errors = eachForm._errors.setdefault(
                                    amount,
                                    ErrorList())
                                errors.append(u'Financial Milestone amount \
                                            cannot be 0')
                            if float(projectTotal) != float(totalRate):
                                errors = eachForm._errors.setdefault(
                                    totalRate,
                                    ErrorList())
                                errors.append(u'Total amount must be \
                                                equal to project value')
        return form

    def get_context_data(self, form, **kwargs):
        context = super(CreateProjectWizard, self).get_context_data(
            form=form, **kwargs)
        if self.steps.current == 'Basic Information':
            ptId = self.storage.get_step_data('Define Project')[
                'Define Project-projectType'
            ]
            data = {'pt': projectType.objects.get(id=int(ptId)).description}
            context.update(data)
        if self.steps.current == 'Define Project':
            if form.is_valid():
                bookId = form.cleaned_data['book']
                chapters = form.cleaned_data['chapters']
                chapterId = [int(eachChapter.id) for eachChapter in chapters]
                data = {'bookId': bookId.id, 'chapterId': chapterId}
                context.update(data)

        if self.steps.current == 'Financial Milestones':
            projectTotal = self.storage.get_step_data('Define Project')[
                'Define Project-totalValue'
            ]
            context.update({'totalValue': projectTotal})
        if self.steps.current == 'Define Team':
            if hasattr(self.request.user, 'employee'):
                locationId = self.request.user.employee.location
                holidays = Holiday.objects.filter(
                    location=locationId
                ).values('name', 'date')
                holidays = Holiday.objects.all().values('name', 'date')
                for holiday in holidays:
                    holiday['date'] = int(
                        holiday['date'].strftime("%s")) * 1000
                data = {'data': list(holidays)}
            else:
                data = {'data': ''}
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
        chapterIdList = [eachRec.id for eachRec in basicInfo['chapters']]
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
            cleanedTeamData.append(changedTeamData.copy())
            changedTeamData.clear()

        if [form.cleaned_data for form in form_list][1]['internal'] is False:
            for milestoneData in [form.cleaned_data for form in form_list][3]:
                milestoneDataCounter += 1
                for k, v in milestoneData.iteritems():
                    k = "{0}-{1}".format(k, milestoneDataCounter)
                    changedMilestoneData[k] = v
                milestoneDate = 'milestoneDate-{0}'.format(
                    milestoneDataCounter)
                changedMilestoneData[milestoneDate] = changedMilestoneData.get(
                    milestoneDate
                ).strftime('%Y-%m-%d')
                DELETE = 'DELETE-{0}'.format(milestoneDataCounter)
                del changedMilestoneData[DELETE]
                cleanedMilestoneData.append(changedMilestoneData.copy())
                changedMilestoneData.clear()
        if [form.cleaned_data for form in form_list][1]['internal'] is True:
            data = {
                'basicInfo': basicInfo,
                'chapterId': chapterIdList,
                'flagData': flagData,
                'effortTotal': effortTotal,
                'revenueRec': revenueRec,
                'teamMember': cleanedTeamData,
            }
        else:
            data = {
                'basicInfo': basicInfo,
                'chapterId': chapterIdList,
                'flagData': flagData,
                'effortTotal': effortTotal,
                'revenueRec': revenueRec,
                'teamMember': cleanedTeamData,
                'milestone': cleanedMilestoneData
            }
        return render(self.request, 'MyANSRSource/projectSnapshot.html', data)


@login_required
def saveProject(request):
    # NIRANJ : Error checking and reporting is missing in this function.
    # Please go back and clean up error handling - for example a int() call
    # with throw ValueError.  You ahve to handle it.  Once you handle how do
    # you send them back to the summary page?

    if request.method == 'POST':
        try:
            pr = Project()
            pr.name = request.POST.get('name')
            pType = projectType.objects.get(
                id=int(request.POST.get('projectType'))
            )
            pr.projectType = pType
            pr.maxProductivityUnits = float(
                request.POST.get('maxProductivityUnits'))
            pr.startDate = request.POST.get('startDate')
            pr.endDate = request.POST.get('endDate')
            pr.totalValue = float(request.POST.get('totalValue'))
            pr.plannedEffort = int(request.POST.get('plannedEffort'))
            pr.currentProject = request.POST.get('currentProject')
            pr.signed = (request.POST.get('signed') == 'True')
            pr.internal = (request.POST.get('internal') == 'True')
            pr.contingencyEffort = int(request.POST.get('contingencyEffort'))
            pr.projectManager = request.user
            pr.bu = CompanyMaster.models.BusinessUnit.objects.get(
                pk=int(request.POST.get('bu'))
            )
            pr.customer = CompanyMaster.models.Customer.objects.get(
                pk=int(request.POST.get('customer'))
            )
            pr.book = Book.objects.get(
                pk=int(request.POST.get('book'))
            )

            projectIdPrefix = "{0}_{1}_{2}".format(
                pr.customer.customerCode,
                datetime.now().year,
                str(pr.customer.seqNumber).zfill(4)
            )

            pr.projectId = projectIdPrefix
            pr.save()
            pr.customer.seqNumber = pr.customer.seqNumber + 1
            pr.customer.save()
            for eachId in eval(request.POST.get('chapters')):
                pr.chapters.add(eachId)
        except ValueError as e:
            messages.error(request, 'DataConversion Error:' + str(e))

        try:
            memberTotal = int(request.POST.get('teamMemberTotal')) + 1

            for memberCount in range(1, memberTotal):
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
                ptm.role = employee.models.Designation.objects.get(
                    pk=request.POST.get(role)
                )
                ptm.plannedEffort = request.POST.get(plannedEffort)
                ptm.rate = request.POST.get(rate)
                ptm.startDate = request.POST.get(startDate)
                ptm.endDate = request.POST.get(endDate)
                ptm.save()
        except ValueError as e:
            messages.error(request, 'DataConversion Error:' + str(e))

        if pr.internal is False:
            milestoneTotal = int(request.POST.get('milestoneTotal')) + 1
            for milestoneCount in range(1, milestoneTotal):
                try:
                    pms = ProjectMilestone()
                    pms.project = pr
                    milestoneDate = 'milestoneDate-{0}'.format(milestoneCount)
                    description = 'description-{0}'.format(milestoneCount)
                    amount = 'amount-{0}'.format(milestoneCount)
                    financial = 'financial-{0}'.format(milestoneCount)
                    date = datetime.strptime(request.POST.get(milestoneDate),
                                             '%Y-%m-%d')
                    pms.milestoneDate = date
                    pms.description = request.POST.get(description)
                    pms.financial = (request.POST.get(financial) == 'True')
                    pms.amount = float(request.POST.get(amount))
                    pms.save()
                # Assuming any of the data conversions fail
                except ValueError as e:
                    # We cannot save a bad record we simply skip over
                    messages.error(request, 'DataConversion Error:' + str(e))

        data = {'projectCode':  projectIdPrefix, 'projectId': pr.id,
                'projectName': pr.name, 'customerId': pr.customer.id}
        return render(request, 'MyANSRSource/projectSuccess.html', data)
    # This is not a post request.  This cannot be possible unless someone is
    # trying to hack things.  Let us just send them back to dashboard.
    else:
        return HttpResponseRedirect(request, '/myansrsource/dashboard')

createProject = CreateProjectWizard.as_view(FORMS)


@login_required
def WrappedCreateProjectView(request):
    return createProject(request)


@login_required
def notify(request):
    projectId = int(request.POST.get('projectId'))
    projectDetails = Project.objects.get(
        id=projectId,
    )
    projectHead = CompanyMaster.models.Customer.objects.filter(
        id=int(request.POST.get('customer')),
    ).values('relatedMember__email',
             'relatedMember__first_name',
             'relatedMember__last_name')
    for eachHead in projectHead:
        if eachHead['relatedMember__email'] != '':
            send_templated_mail(
                template_name='projectCreatedHeadEmail',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[eachHead['relatedMember__email'], ],
                context={
                    'first_name': eachHead['relatedMember__first_name'],
                    'projectId': projectId,
                    'pmname': projectDetails.projectManager,
                    'startDate': projectDetails.startDate
                    },
            )
    teamMembers = ProjectTeamMember.objects.filter(
        project__id=projectId
    ).values('member__email', 'member__first_name',
             'member__last_name', 'startDate')
    for eachMember in teamMembers:
        if eachMember['member__email'] != '':
            send_templated_mail(
                template_name='projectCreatedTextEmail',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[eachMember['member__email'], ],
                context={
                    'first_name': eachMember['member__first_name'],
                    'projectId': projectId,
                    'pmname': projectDetails.projectManager,
                    'startDate': projectDetails.startDate,
                    'mystartdate': eachMember['startDate']
                    },
            )
    projectName = request.POST.get('projectName')
    data = {'projectCode': request.POST.get('projectCode'),
            'projectName': projectName,
            'notify': 'F'}
    return render(request, 'MyANSRSource/projectSuccess.html', data)


@login_required
def deleteProject(request):
    ProjectBasicInfoForm()
    ProjectTeamForm()
    ProjectMilestoneForm()
    return HttpResponseRedirect('add')


@login_required
def ViewProject(request):
    if request.method == 'POST':
        projectId = int(request.POST.get('project'))
        projectObj = Project.objects.filter(id=projectId)
        basicInfo = projectObj.values(
            'projectType__description', 'bu__name', 'customer__name',
            'name', 'startDate', 'endDate', 'book__name',
            'plannedEffort', 'contingencyEffort',
            'totalValue'
        )[0]
        flagData = projectObj.values(
            'maxProductivityUnits', 'signed', 'internal', 'currentProject'
        )[0]
        cleanedTeamData = ProjectTeamMember.objects.filter(
            project=projectObj).values(
            'member__username', 'role', 'startDate', 'endDate',
            'plannedEffort', 'rate'
            )
        chapters = projectObj.values('chapters__name')
        if flagData['internal']:
            cleanedMilestoneData = []
        else:
            cleanedMilestoneData = ProjectMilestone.objects.filter(
                project=projectObj).values('milestoneDate', 'description',
                                           'amount')
        data = {
            'basicInfo': basicInfo,
            'chapters': chapters,
            'flagData': flagData,
            'teamMember': cleanedTeamData,
            'milestone': cleanedMilestoneData
        }
        return render(request, 'MyANSRSource/viewProjectSummary.html', data)
    data = Project.objects.filter(projectManager=request.user).values(
        'name', 'id'
    )
    return render(request, 'MyANSRSource/viewProject.html', {'projects': data})


def GetChapters(request, bookid):
    chapters = Chapter.objects.filter(book__id=bookid)
    json_chapters = serializers.serialize("json", chapters)
    return HttpResponse(json_chapters, content_type="application/javascript")


def GetProjectType(request):
    # NIRANJ: Why is this being filtered from Project Team member and not
    # project directly?  this will result in duplicate records.
    typeData = ProjectTeamMember.objects.values(
        'project__id',
        'project__name',
        'project__projectType__code',
        'project__maxProductivityUnits',
        'project__projectType__description'
    ).filter(project__closed=False)
    for eachData in typeData:
        eachData['project__maxProductivityUnits'] = float(
            eachData['project__maxProductivityUnits'])
    data = {'data': list(typeData)}
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type="application/json")


def csrf_failure(request, reason=""):
    return render(request, 'MyANSRSource/csrfFailure.html', {'reason': reason})


def Logout(request):
    logout(request)
    request.session.flush()
    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
    return HttpResponseRedirect('/myansrsource')
