import logging
logger = logging.getLogger('MyANSRSource')
import json
from collections import OrderedDict

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
from django.utils.timezone import utc

from templated_email import send_templated_mail

from MyANSRSource.models import Project, TimeSheetEntry, \
    ProjectMilestone, ProjectTeamMember, Book, ProjectChangeInfo, \
    Chapter, projectType, Task, ProjectManager

from MyANSRSource.forms import LoginForm, ProjectBasicInfoForm, \
    ProjectTeamForm, ActivityForm, TimesheetFormset, ProjectFlagForm, \
    ChangeProjectBasicInfoForm, ChangeProjectTeamMemberForm, \
    ChangeProjectForm, CloseProjectMilestoneForm

import CompanyMaster
import employee
from CompanyMaster.models import Holiday


from ldap import LDAPError
# views for ansr

FORMS = [
    ("Define Project", ProjectBasicInfoForm),
    ("Basic Information", ProjectFlagForm),
]
TEMPLATES = {
    "Define Project": "MyANSRSource/projectDefinition.html",
    "Basic Information": "MyANSRSource/projectBasicInfo.html",
}

CFORMS = [
    ("My Projects", ChangeProjectForm),
    ("Change Basic Information", ChangeProjectBasicInfoForm),
]
CTEMPLATES = {
    "My Projects": "MyANSRSource/changeProject.html",
    "Change Basic Information": "MyANSRSource/changeProjectBasicInfo.html",
}

TMFORMS = [
    ("My Projects", ChangeProjectForm),
    ("Manage Milestones", formset_factory(
        CloseProjectMilestoneForm,
        extra=1,
        max_num=1,
        can_delete=True
    )),
]
TMTEMPLATES = {
    "My Projects": "MyANSRSource/manageMilestone.html",
    "Manage Milestones": "MyANSRSource/manageProjectMilestone.html",
}

MEMBERFORMS = [
    ("My Projects", ChangeProjectForm),
    ("Manage Team", formset_factory(
        ChangeProjectTeamMemberForm,
        extra=1,
        max_num=1,
        can_delete=True
    )),
]
MEMBERTEMPLATES = {
    "My Projects": "MyANSRSource/manageProjectTeam.html",
    "Manage Team": "MyANSRSource/manageProjectMember.html",
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
                    approved = False
                    for k, v in timesheet.cleaned_data.iteritems():
                        if k == 'tsId':
                            if v:
                                approved = TimeSheetEntry.objects.get(
                                    pk=v).approved
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
                        timesheetDict['approved'] = approved
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
                        update = 1
                    else:
                        nonbillableTS = TimeSheetEntry()
                        update = 0
                    # Common values for Billable and Non-Billable
                    nonbillableTS.wkstart = changedStartDate
                    nonbillableTS.wkend = changedEndDate
                    nonbillableTS.teamMember = request.user
                    if update:
                        if 'save' not in request.POST:
                            nonbillableTS.hold = True
                    else:
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
                for eachTimesheet in timesheetList:
                    if eachTimesheet['tsId'] > 0:
                        billableTS = TimeSheetEntry.objects.filter(
                            id=eachTimesheet['tsId']
                        )[0]
                        update = 1
                    else:
                        billableTS = TimeSheetEntry()
                        update = 0
                    billableTS.wkstart = changedStartDate
                    billableTS.wkend = changedEndDate
                    billableTS.teamMember = request.user
                    if update:
                        if 'save' not in request.POST:
                            billableTS.hold = True
                    else:
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
                        if k != 'hold':
                            setattr(billableTS, k, v)
                    billableTS.save()
                    eachTimesheet['tsId'] = billableTS.id
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
                    nonbillableTS.activity = eachActivity['activity']
                    nonbillableTS.teamMember = request.user
                    if 'save' not in request.POST:
                        nonbillableTS.approved = True
                        nonbillableTS.managerFeedback = 'System Approved'
                        nonbillableTS.hold = True
                        nonbillableTS.approvedon = datetime.now().replace(
                            tzinfo=utc)
                    else:
                        nonbillableTS.approved = False
                        nonbillableTS.hold = False
                    for k, v in eachActivity.iteritems():
                        if k != 'hold' and k != 'approved':
                            setattr(nonbillableTS, k, v)
                    nonbillableTS.save()
                    eachActivity['atId'] = nonbillableTS.id
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
                    if 'save' not in request.POST:
                        billableTS.approved = True
                        billableTS.managerFeedback = 'System Approved'
                        billableTS.hold = True
                        billableTS.approvedon = datetime.now().replace(
                            tzinfo=utc)
                    else:
                        billableTS.approved = False
                        billableTS.hold = False
                    for k, v in eachTimesheet.iteritems():
                        if k != 'hold' and k != 'approved':
                            setattr(billableTS, k, v)
                    billableTS.save()
                    eachTimesheet['tsId'] = billableTS.id
            dates = switchWeeks(request)
            for eachtsList in timesheetList:
                ts = TimeSheetEntry.objects.get(pk=eachtsList['tsId'])
                eachtsList['hold'] = ts.hold
            tsContent = timesheetList
            atContent = activitiesList
            tsErrorList = []
            atErrorList = []
            msg = ''

            for eachTS in tsContent:
                tsObj = TimeSheetEntry.objects.get(pk=eachTS['tsId'])
                if eachTS['approved']:
                    msg += '{0} - is approved, '.format(tsObj.project.name)
                elif eachTS['hold']:
                    if tsObj.approved:
                        msg += '{0} - is auto approved by system'.format(
                            tsObj.project.name)
                    else:
                        msg += '{0} - is sent for approval \
                            to your manager'.format(tsObj.project.name)
                elif 'save' in request.POST:
                    msg += '{0} - timesheet is saved'.format(tsObj.project.name)

            messages.info(request, msg)
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
            atErrorList = activities.errors
            atContent = [k.cleaned_data for k in activities]

        # Constructing status of timesheet

        data = {'weekstartDate': dates['start'],
                'weekendDate': dates['end'],
                'disabled': dates['disabled'],
                'extra': 0,
                'tsErrorList': tsErrorList,
                'atErrorList': atErrorList,
                'tsFormList': tsContent,
                'atFormList': atContent}
        return renderTimesheet(request, data)
    else:
        # Switch dates back and forth
        dates = switchWeeks(request)

        # Getting Data for timesheet and activity
        tsDataList = getTSDataList(request, dates['start'], dates['end'])

        # Common values initialization
        extra = 0

        # Approved TS data
        if len(tsDataList['tsData']):
            tsFormList = tsDataList['tsData']
            atFormList = tsDataList['atData']

        # Fresh TS data
        else:
            tsFormList, atFormList = [], []
            extra = 1
            messages.success(request, 'Please enter your timesheet for \
                             this week')

        # Constructing status of timesheet

        msg = ''

        for eachTS in tsFormList:
            tsObj = TimeSheetEntry.objects.get(pk=eachTS['tsId'])
            if eachTS['approved']:
                msg += '{0} - is approved, '.format(tsObj.project.name)
            elif eachTS['hold']:
                msg += '{0} - is sent for approval \
                    to your manager'.format(tsObj.project.name)
            elif 'save' in request.POST:
                msg += '{0} - timesheet is saved'.format(tsObj.project.name)
            else:
                msg += '{0} - Rework on your timesheet'.format(
                    tsObj.project.name)

        messages.info(request, msg)

        data = {'weekstartDate': dates['start'],
                'weekendDate': dates['end'],
                'disabled': dates['disabled'],
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
def getTSDataList(request, weekstartDate, ansrEndDate):
    # To be approved TS data
    cwActivityData = TimeSheetEntry.objects.filter(
        Q(
            wkstart=weekstartDate,
            wkend=ansrEndDate,
            teamMember=request.user,
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


def renderTimesheet(request, data):
    tsObj = TimeSheetEntry.objects.filter(
        wkstart=data['weekstartDate'],
        wkend=data['weekendDate'],
        teamMember=request.user,
        approved=False
    )
    billableHours = tsObj.filter(
        activity__isnull=True,
        task__taskType='B'
    ).values('totalH')
    idleHours = tsObj.filter(
        activity__isnull=True,
        task__taskType='I'
    ).values('totalH')
    othersHours = tsObj.filter(
        project__isnull=True
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

    attendanceObj = employee.models.Attendance.objects.filter(
        employee__employee_assigned_id=request.user.id,
        attdate__range=[data['weekstartDate'], data['weekendDate']]
    )
    attendance = {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0}
    for eachObj in attendanceObj:
        if eachObj.swipe_out is not None or eachObj.swipe_in is not None:
            timediff = eachObj.swipe_out - eachObj.swipe_in
            atttime = "{0}:{1}".format(timediff.seconds // 3600,
                                       (timediff.seconds % 3600) // 60)
            attendance['{0}'.format(eachObj.attdate.weekday())] = atttime

    attendance = OrderedDict(sorted(attendance.items(), key=lambda t: t[0]))

    finalData = {'weekstartDate': data['weekstartDate'],
                 'weekendDate': data['weekendDate'],
                 'disabled': data['disabled'],
                 'shortDays': ['Mon', 'Tue', 'Wed', 'Thu',
                               'Fri', 'Sat', 'Sun'],
                 'billableHours': billableHours,
                 'idleHours': idleHours,
                 'bTotal': bTotal,
                 'idleTotal': idleTotal,
                 'attendance': attendance,
                 'othersTotal': othersTotal,
                 'tsFormset': tsFormset,
                 'atFormset': atFormset}
    if 'tsErrorList' in data:
        finalData['tsErrorList'] = data['tsErrorList']
    if 'atErrorList' in data:
        finalData['atErrorList'] = data['atErrorList']
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

    totalCurrentProjects = ProjectTeamMember.objects.filter(
        member=request.user,
        project__closed=False
    ).count()

    cp = totalActiveProjects + totalCurrentProjects

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
        'batch', 'exercise', 'trainingDate')
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
        'cp': cp,
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
                    logger.error(
                        'User {0} permission details {1} group perms'.format(
                            user.username,
                            user.get_all_permissions(),
                            user.get_group_permissions()))
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
            form.fields['project'].queryset = Project.objects.filter(
                closed=False,
                projectManager=self.request.user
            )
        if step == 'Manage Milestones':
            for eachForm in form:
                eachForm.fields['DELETE'].widget.attrs[
                    'class'
                ] = 'form-control'

        return form

    def get_form_initial(self, step):
        projectMS = {}
        if step == 'Manage Milestones':
            selectedProjectId = self.storage.get_step_data(
                'My Projects'
            )['My Projects-project']
            projectMS = ProjectMilestone.objects.filter(
                project__id=selectedProjectId,
            ).values(
                'id',
                'financial',
                'milestoneDate',
                'description',
                'amount',
                'closed'
            )
        return self.initial_dict.get(step, projectMS)

    def done(self, form_list, **kwargs):
        milestoneData = [form.cleaned_data for form in form_list][1]
        projectObj = [form.cleaned_data for form in form_list][0]['project']

        if projectObj:
            for eachData in milestoneData:
                if eachData['id']:
                    pm = ProjectMilestone.objects.get(id=eachData['id'])
                    if eachData['DELETE']:
                        pm.delete()
                    else:
                        saveData(self, pm, eachData, projectObj)
                else:
                    pm = ProjectMilestone()
                    if eachData['DELETE']:
                        pass
                    else:
                        saveData(self, pm, eachData, projectObj)
        else:
            logging.error("Request: " + self.request)
        return HttpResponseRedirect('/myansrsource/dashboard')


def saveData(self, pm, eachData, projectObj):
    if pm.closed:
        pass
    else:
        pm.project = projectObj
        pm.description = eachData['description']
        pm.financial = eachData['financial']
        pm.milestoneDate = eachData['milestoneDate']
        pm.amount = eachData['amount']
        pm.closed = eachData['closed']
        pm.save()

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
        if self.steps.current == 'Change Basic Information':
            currentProject = Project.objects.get(
                pk=self.storage.get_step_data(
                    'My Projects'
                )['My Projects-project'])
            totalEffort = currentProject.plannedEffort
            context.update({'totalEffort': totalEffort})
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
    """
    try:
        prc = newInfo[0]['project']
        oldCost = prc.totalValue
        oldEffort = prc.plannedEffort
        prc.plannedEffort = newInfo[1]['revisedEffort']
        prc.totalValue = newInfo[1]['revisedTotal']
        prc.closed = newInfo[1]['closed']
        prc.signed = newInfo[1]['signed']
        prc.save()

        pci = ProjectChangeInfo()
        pci.project = prc
        pci.reason = newInfo[1]['reason']
        pci.endDate = newInfo[1]['endDate']
        pci.revisedEffort = oldEffort
        pci.revisedTotal = oldCost
        pci.closed = newInfo[1]['closed']
        if pci.closed is True:
            pci.closedOn = datetime.now()
        pci.signed = newInfo[1]['signed']
        pci.save()

        # We need the Primary key to create the CRId
        pci.crId = "CR-{0}".format(pci.id)
        pci.save()

        return {'crId': pci.crId}
    except (ProjectTeamMember.DoesNotExist,
            ProjectMilestone.DoesNotExist) as e:
        messages.error(request, 'Could not save change request information')
        logger.error('Exception in UpdateProjectInfo :' + str(e))
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
        if step == 'Basic Information':
            signed = self.storage.get_step_data('Define Project')[
                'Define Project-signed'
            ]
            if signed == 'False':
                form.fields['po'].widget.attrs[
                    'readonly'
                ] = 'True'
            if form.is_valid():
                self.request.session['PStartDate'] = form.cleaned_data[
                    'startDate'
                ].strftime('%Y-%m-%d')
                self.request.session['PEndDate'] = form.cleaned_data[
                    'endDate'
                ].strftime('%Y-%m-%d')

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

        if self.steps.current == 'Financial Milestones':
            projectTotal = self.storage.get_step_data('Basic Information')[
                'Basic Information-totalValue'
            ]
            context.update({'totalValue': projectTotal})

        return context

    def done(self, form_list, **kwargs):
        basicInfo = [form.cleaned_data for form in form_list][0]
        pm = [int(pm.id) for pm in basicInfo['projectManager']]
        flagData = {}
        for k, v in [form.cleaned_data for form in form_list][1].iteritems():
            if k == 'startDate':
                flagData['displayStartDate'] = v.strftime('%Y-%m-%d')
                flagData['startDate'] = int(v.strftime('%s'))
            elif k == 'endDate':
                flagData['displayEndDate'] = v.strftime('%Y-%m-%d')
                flagData['endDate'] = int(v.strftime('%s'))
            else:
                flagData[k] = v
        effortTotal = 0

        if flagData['plannedEffort']:
            revenueRec = flagData['totalValue'] / flagData['plannedEffort']
        else:
            revenueRec = 0
        data = {
            'basicInfo': basicInfo,
            'pm': pm,
            'flagData': flagData,
            'effortTotal': effortTotal,
            'revenueRec': revenueRec,
        }
        return render(self.request, 'MyANSRSource/projectSnapshot.html', data)


class ManageTeamWizard(SessionWizardView):

    def get_template_names(self):
        return [MEMBERTEMPLATES[self.steps.current]]

    def get_form_initial(self, step):
        currentProject = []
        if step == 'Manage Team':
            projectId = self.storage.get_step_data(
                'My Projects')['My Projects-project']
            if projectId is not None:
                currentProject = ProjectTeamMember.objects.filter(
                    project__id=projectId).values('id', 'member', 'role',
                                                  'startDate', 'endDate',
                                                  'plannedEffort', 'rate'
                                                  )
            else:
                logging.error("Project Id : {0}, Request: {1},".format(
                    projectId, self.request))
        return self.initial_dict.get(step, currentProject)

    def get_context_data(self, form, **kwargs):
        context = super(ManageTeamWizard, self).get_context_data(
            form=form, **kwargs)
        if self.steps.current == 'My Projects':
            form.fields['project'].queryset = Project.objects.filter(
                projectManager=self.request.user,
                closed=False
            )
        if self.steps.current == 'Manage Team':
            for eachForm in form:
                eachForm.fields['DELETE'].widget.attrs[
                    'class'
                ] = 'form-control'
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

    def done(self, form_list, **kwargs):
        for eachData in [form.cleaned_data for form in form_list][1]:
            if None in eachData.values():
                pass
            else:
                if eachData['id']:
                    if eachData['DELETE']:
                        ProjectTeamMember.objects.get(
                            pk=eachData['id']).delete()
                    else:
                        ptm = ProjectTeamMember.objects.get(pk=eachData['id'])
                else:
                    ptm = ProjectTeamMember()

                ptm.project = [
                    form.cleaned_data for form in form_list][0]['project']
                del(eachData['id'])
                for k, v in eachData.iteritems():
                    setattr(ptm, k, v)
                ptm.save()
                teamMembers = ProjectTeamMember.objects.filter(
                    project__id=ptm.project.id
                ).values('member__email', 'member__first_name',
                         'member__last_name', 'startDate', 'role__name')
                pm = ProjectManager.objects.filter(
                    project__id=ptm.project.id
                ).values('user__first_name', 'user__last_name')
                l = []
                for eachManager in pm:
                    name = eachManager[
                        'user__first_name'] + "  " + eachManager[
                            'user__last_name']
                    l.append(name)
                if len(l) > 1:
                    manager = ",".join(l)
                else:
                    manager = "  ".join(l)
                for eachMember in teamMembers:
                    if eachMember['member__email'] != '':
                        send_templated_mail(
                            template_name='projectCreatedTeam',
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[
                                eachMember['member__email'],
                                ],
                            context={
                                'first_name': eachMember['member__first_name'],
                                'projectId': ptm.project.id,
                                'projectName': ptm.project.name,
                                'pmname': manager,
                                'startDate': ptm.project.startDate,
                                'mystartdate': eachMember['startDate'],
                                'myrole': eachMember['role__name'],
                                },
                            )
        return HttpResponseRedirect('/myansrsource/dashboard')


manageTeam = ManageTeamWizard.as_view(MEMBERFORMS)


@login_required
def WrappedManageTeamView(request):
    return manageTeam(request)


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
            startDate = datetime.fromtimestamp(
                int(request.POST.get('startDate'))).date()
            endDate = datetime.fromtimestamp(
                int(request.POST.get('endDate'))).date()
            pr.startDate = startDate
            pr.endDate = endDate
            pr.po = request.POST.get('po')
            pr.totalValue = float(request.POST.get('totalValue'))
            pr.plannedEffort = int(request.POST.get('plannedEffort'))
            pr.currentProject = request.POST.get('currentProject')
            pr.signed = (request.POST.get('signed') == 'True')
            pr.internal = (request.POST.get('internal') == 'True')
            pr.contingencyEffort = int(request.POST.get('contingencyEffort'))
            pr.bu = CompanyMaster.models.BusinessUnit.objects.get(
                pk=int(request.POST.get('bu'))
            )
            pr.customer = CompanyMaster.models.Customer.objects.get(
                pk=int(request.POST.get('customer'))
            )
            pr.book = Book.objects.get(
                pk=int(request.POST.get('book'))
            )

            projectIdPrefix = "{0}-{1}-{2}".format(
                pr.customer.customerCode,
                datetime.now().year,
                str(pr.customer.seqNumber).zfill(3)
            )

            pr.projectId = projectIdPrefix
            pr.save()
            pr.customer.seqNumber = pr.customer.seqNumber + 1
            pr.customer.save()

            for eachId in eval(request.POST.get('pm')):
                pm = ProjectManager()
                pm.user = User.objects.get(pk=eachId)
                pm.project = pr
                pm.save()
        except ValueError as e:
            logger.exception(e)
            return render(
                request,
                'MyANSRSource/projectCreationFailure.html',
                {})

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
    projectName = request.POST.get('projectName')
    projectDetails = Project.objects.get(
        pk=projectId,
    )
    pm = ProjectManager.objects.filter(
        project__id=projectId
    ).values('user__first_name', 'user__last_name')
    l = []
    for eachManager in pm:
        name = eachManager[
            'user__first_name'] + "  " + eachManager['user__last_name']
        l.append(name)
    if len(l) > 1:
        manager = ",".join(l)
    else:
        manager = "  ".join(l)
    projectHead = CompanyMaster.models.Customer.objects.filter(
        id=int(request.POST.get('customer')),
    ).values('relatedMember__email',
             'relatedMember__first_name',
             'relatedMember__last_name')
    for eachHead in projectHead:
        if eachHead['relatedMember__email'] != '':
            send_templated_mail(
                template_name='projectCreatedMgmt',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[
                    eachHead['relatedMember__email'],
                    ],
                context={
                    'first_name': eachHead['relatedMember__first_name'],
                    'projectId': projectDetails.projectId,
                    'projectName': projectName,
                    'pmname': manager,
                    'startDate': projectDetails.startDate},
                )
    data = {'projectCode': request.POST.get('projectCode'),
            'projectName': projectName,
            'notify': 'F'}
    return render(request, 'MyANSRSource/projectSuccess.html', data)


@login_required
def deleteProject(request):
    ProjectBasicInfoForm()
    ProjectTeamForm()
    return HttpResponseRedirect('add')


@login_required
def ViewProject(request):
    if request.method == 'POST':
        projectId = int(request.POST.get('project'))
        projectObj = Project.objects.filter(id=projectId)
        basicInfo = projectObj.values(
            'projectType__description', 'bu__name', 'customer__name',
            'name', 'book__name', 'signed', 'internal', 'currentProject'
        )[0]
        flagData = projectObj.values(
            'startDate', 'endDate', 'plannedEffort', 'contingencyEffort',
            'totalValue', 'maxProductivityUnits', 'po'
        )[0]
        cleanedTeamData = ProjectTeamMember.objects.filter(
            project=projectObj).values(
            'member__username', 'role', 'startDate', 'endDate',
            'plannedEffort', 'rate'
            )
        if basicInfo['internal']:
            cleanedMilestoneData = []
        else:
            cleanedMilestoneData = ProjectMilestone.objects.filter(
                project=projectObj).values('milestoneDate', 'description',
                                           'amount')

        changeTracker = ProjectChangeInfo.objects.filter(
            project=projectObj).values(
            'reason', 'endDate', 'revisedEffort', 'revisedTotal',
            'closed', 'closedOn', 'signed'
        )
        data = {
            'basicInfo': basicInfo,
            'flagData': flagData,
            'teamMember': cleanedTeamData,
            'milestone': cleanedMilestoneData,
            'changes': changeTracker
        }
        return render(request, 'MyANSRSource/viewProjectSummary.html', data)
    data = Project.objects.filter(projectManager=request.user).values(
        'name', 'id', 'closed'
    )
    return render(request, 'MyANSRSource/viewProject.html', {'projects': data})


def GetChapters(request, bookid):
    chapters = Chapter.objects.filter(book__id=bookid)
    json_chapters = serializers.serialize("json", chapters)
    return HttpResponse(json_chapters, content_type="application/javascript")


def GetTasks(request, projectid):
    tasks = Task.objects.filter(
        projectType=Project.objects.get(pk=projectid).projectType
    ).values('code', 'name', 'id')
    data = {'data': list(tasks)}
    return HttpResponse(json.dumps(data), content_type="application/javascript")


def GetHolidays(request, memberid):
    currentUser = User.objects.get(pk=memberid)
    if hasattr(currentUser, 'employee'):
        locationId = currentUser.employee.location
        holidayList = Holiday.objects.filter(
            location=locationId
        ).values('name', 'date')
        for holiday in holidayList:
            holiday['date'] = int(
                holiday['date'].strftime("%s")) * 1000
        data = {'data': list(holidayList)}
    else:
        data = {'data': ''}
    return HttpResponse(json.dumps(data), content_type="application/javascript")


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
