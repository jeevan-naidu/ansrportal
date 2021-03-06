import logging
logger = logging.getLogger('MyANSRSource')
import json
from collections import OrderedDict
from django.contrib.auth.decorators import permission_required

from django.forms.utils import ErrorList
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.contrib import auth, messages
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from formtools.wizard.views import SessionWizardView
from django.forms.formsets import formset_factory
from datetime import datetime, timedelta, date
from django.db.models import Q, Sum
from django.utils.timezone import utc
from django.conf import settings
from employee.models import Employee


from fb360.models import Respondent


from MyANSRSource.models import Project, TimeSheetEntry, \
    ProjectMilestone, ProjectTeamMember, Book, ProjectChangeInfo, \
    Chapter, projectType, Task, ProjectManager, SendEmail, BTGReport

from MyANSRSource.forms import LoginForm, ProjectBasicInfoForm, \
    ActivityForm, TimesheetFormset, ProjectFlagForm, \
    ChangeProjectBasicInfoForm, ChangeProjectTeamMemberForm, \
    MyRemainderForm, ChangeProjectForm, CloseProjectMilestoneForm, \
    changeProjectLeaderForm, BTGReportForm

import CompanyMaster
import employee
from employee.models import Remainder
from CompanyMaster.models import Holiday, HRActivity
from Grievances.models import Grievances


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

TLFORMS = [
    ("My Projects", ChangeProjectForm),
    ("Manage Project Leader", changeProjectLeaderForm),
]
TLTEMPLATES = {
    "My Projects": "MyANSRSource/manageProjectLead.html",
    "Manage Project Leader": "MyANSRSource/manageProjectTeamLead.html",
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

days = ['monday', 'tuesday', 'wednesday', 'thursday',
        'friday', 'saturday', 'sunday']


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


def append_tsstatus_msg(request, tsSet, msg):
    messages.info(request, msg + str(tsSet))


def get_mondays_list_till_date():
    '''generate all days that are Mondays in the current year
    returns only monday(date object)'''
    current_date = datetime.now().date()
    jan1 = date(current_date.year, 1, 1)


    # find first Monday (which could be this day)
    monday = jan1 + timedelta(days=(7 - jan1.weekday()) % 7)

    while 1:

        if monday.year != current_date.year or monday > current_date:
            break
        yield monday
        monday += timedelta(days=7)

# diff between above function get_mondays_list_till_date() and below function weeks_list_till_date
# is only in the yield statement
#
def weeks_list_till_date():
    '''generate week(monday to sunday) for the current year
    returns tuple for with 2 objects: week_start and week_end'''
    current_date = datetime.now().date()

    jan1 = date(current_date.year, 1, 1)

    # find first Monday (which could be this day)
    monday = jan1 + timedelta(days=(7 - jan1.weekday()) % 7)

    while 1:

        if monday.year != current_date.year or monday > current_date:
            break
        yield (monday, monday + timedelta(days=6))
        monday += timedelta(days=7)


@login_required
@permission_required('MyANSRSource.enter_timesheet')
def Timesheet(request):
    # Creating Formset
    # Week Calculation.
    leaveDayWork = False
    # Getting the form values and storing it to DB.


    if request.method == 'POST':
        # Getting the forms with submitted values
        hold_button = False

        # for timesheet bug which showed project not available  error message by vivek
        tmp_date = datetime.now().date()
        tmp_date -= timedelta(days=7)
        endDate1 = request.GET.get('enddate', '')
        if request.GET.get("week") == 'prev':
            if endDate1:
                tmp_date = datetime(year=int(endDate1[4:8]), month=int(endDate1[2:4]), day=int(endDate1[0:2]))
                tmp_date -= timedelta(days=13)

        elif request.GET.get("week") == 'next':
            if endDate1:
                tmp_date = datetime(year=int(endDate1[4:8]), month=int(endDate1[2:4]), day=int(endDate1[0:2]))
                tmp_date += timedelta(days=1)
        #  fix ends here

        tsform = TimesheetFormset(request.user, tmp_date)
        tsFormset = formset_factory(
            tsform, extra=1, max_num=1, can_delete=True
        )
        atFormset = formset_factory(
            ActivityForm, extra=1, max_num=1, can_delete=True
        )
        timesheets = tsFormset(request.POST)
        activities = atFormset(request.POST, prefix='at')
        dbSave = False

        # User values for timsheet
        if timesheets.is_valid() and activities.is_valid():
            changedStartDate = datetime.strptime(
                request.POST.get('startdate'), '%d%m%Y'
            ).date()
            changedEndDate = datetime.strptime(
                request.POST.get('enddate'), '%d%m%Y'
            ).date()
            mondayTotal = float(0.0)
            tuesdayTotal = float(0.0)
            wednesdayTotal = float(0.0)
            thursdayTotal = float(0.0)
            fridayTotal = float(0.0)
            saturdayTotal = float(0.0)
            sundayTotal = float(0.0)
            weekTotal = float(0.0)
            billableTotal = float(0.0)
            nonbillableTotal = float(0.0)
            weekHolidays = []
            (timesheetList, activitiesList,
             timesheetDict, activityDict) = ([], [], {}, {})
            if hasattr(request.user, 'employee'):
                locationId = request.user.employee.location
                weekHolidays = Holiday.objects.filter(
                    location=locationId,
                    date__range=[changedStartDate, changedEndDate]
                ).values('date')
                weekTotalValidate = 40 - (8 * len(weekHolidays))
                weekTotalValidate = float(weekTotalValidate)
                weekTotalExtra = weekTotalValidate + 4
            else:
                weekHolidays = []
                weekTotalValidate = 40
                weekTotalExtra = 4
            for timesheet in timesheets:
                if timesheet.cleaned_data['DELETE'] is True:
                    TimeSheetEntry.objects.filter(
                        id=timesheet.cleaned_data['tsId']
                    ).delete()
                else:
                    for holiday in weekHolidays:
                        holidayDay = u'{0}H'.format(
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
                            if isinstance(v, float):
                                mondayTotal += float(v)
                            else:
                                mondayTotal += float(0.0)
                        elif k == 'tuesdayH':
                            if isinstance(v, float):
                                tuesdayTotal += float(v)
                            else:
                                tuesdayTotal += float(0.0)
                        elif k == 'wednesdayH':
                            if isinstance(v, float):
                                wednesdayTotal += float(v)
                            else:
                                wednesdayTotal += float(0.0)
                        elif k == 'thursdayH':
                            if isinstance(v, float):
                                thursdayTotal += float(v)
                            else:
                                thursdayTotal += float(0.0)
                        elif k == 'fridayH':
                            if isinstance(v, float):
                                fridayTotal += float(v)
                            else:
                                fridayTotal += float(0.0)
                        elif k == 'saturdayH':
                            if isinstance(v, float):
                                saturdayTotal += float(v)
                            else:
                                saturdayTotal += float(0.0)
                        elif k == 'sundayH':
                            if isinstance(v, float):
                                sundayTotal += float(v)
                            else:
                                sundayTotal += float(0.0)
                        elif k == 'totalH':
                            billableTotal += float(v)
                            weekTotal += float(v)
                        timesheetDict[k] = v
                        timesheetDict['approved'] = approved
                    timesheetList.append(timesheetDict.copy())
                    timesheetDict.clear()
            for activity in activities:
                if activity.cleaned_data['activity'] is not None:
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
                            elif k == 'activity_total':
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
            elif ('save' not in request.POST) and (
                    weekTotal < weekTotalValidate-0.05):
                messages.error(request,
                               u'Your total timesheet activity for \
                               this week is below {0} hours'.format(
                    weekTotalValidate))
            elif (weekTotal > weekTotalExtra) | \
                 (billableTotal > weekTotalExtra) | \
                 (nonbillableTotal > weekTotalValidate) | \
                 (leaveDayWork is True):
                if len(activitiesList):
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
                        if (weekTotal > 40):
                            nonbillableTS.exception = \
                                "Week's total is more than 40 hours"
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
                        global dbSave
                        dbSave = True
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
                    if 'save' not in request.POST:
                        billableTS.hold = True
                    billableTS.billable = True
                    if (weekTotal > 40):
                        billableTS.exception = \
                            "Week's total is more than 40 hours"
                    elif billableTotal > 40:
                        billableTS.exception = \
                            'Billable activity more than 40 Hours'
                    elif leaveDayWork is True:
                        billableTS.exception = 'Worked on Holiday'
                    for k, v in eachTimesheet.iteritems():
                        if k != 'hold':
                            if k in ('mondayQ','tuesdayQ','wednesdayQ','thursdayQ','fridayQ','saturdayQ','sundayQ'):
                                if v==None:
                                    v=float(0.0)
                            if k in ('mondayH','tuesdayH','wednesdayH','thursdayH','fridayH','saturdayH','sundayH'):
                                if v==None:
                                    v=float(0.0)
                            setattr(billableTS, k, v)
                    billableTS.save()
                    global dbSave
                    dbSave = True
                    eachTimesheet['tsId'] = billableTS.id
            else:
                # Save Timesheet
                if len(activitiesList):
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
                        global dbSave
                        dbSave = True
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
                            if k in ('mondayQ','tuesdayQ','wednesdayQ','thursdayQ','fridayQ','saturdayQ','sundayQ'):
                                if v==None:
                                    v=float(0.0)
                            if k in ('mondayH','tuesdayH','wednesdayH','thursdayH','fridayH','saturdayH','sundayH'):
                                if v==None:
                                    v=float(0.0)
                            setattr(billableTS, k, v)
                    billableTS.save()
                    global dbSave
                    dbSave = True
                    eachTimesheet['tsId'] = billableTS.id
            dates = switchWeeks(request)
            for eachtsList in timesheetList:
                if eachtsList['tsId']:
                    ts = TimeSheetEntry.objects.get(pk=eachtsList['tsId'])
                    eachtsList['hold'] = ts.hold
            tsContent = timesheetList
            atContent = activitiesList
            tsErrorList = []
            atErrorList = []

            approvedSet = set()
            autoApprovedSet = set()
            holdSet = set()
            saveSet = set()
            for eachTS in tsContent:
                if eachtsList['tsId']:
                    tsObj = TimeSheetEntry.objects.get(pk=eachTS['tsId'])
                    if eachTS['approved']:
                        approvedSet.add(tsObj.project.projectId)
                    elif eachTS['hold']:
                        if tsObj.approved:
                            autoApprovedSet.add(tsObj.project.projectId)
                        else:
                            holdSet.add(tsObj.project.projectId)
                    elif 'save' in request.POST:
                        saveSet.add(tsObj.project.projectId)

            if len(approvedSet) > 0:
                messages.success(
                    request, 'Timesheet approved :' + str(list(approvedSet)))
                hold_button = True
            if len(autoApprovedSet) > 0:
                messages.success(
                    request, 'Timesheet auto-approved by the system :' +
                    str(list(autoApprovedSet)))
                hold_button = True
            if len(holdSet) > 0:
                messages.info(
                    request, 'Timesheet sent to your manager :' +
                    str(list(holdSet)))
                hold_button = True
            if len(saveSet) > 0:
                messages.info(
                    request, 'Timesheet has been saved:' +
                    str(list(saveSet)))
                hold_button = False
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

        if len(tsContent):
            for eachContent in tsContent:
                if 'project' in eachContent:
                    eachContent['projectType'] = eachContent[
                        'project'].projectType.code

        # Constructing status of timesheet

        data = {'weekstartDate': dates['start'],
                'weekendDate': dates['end'],
                'disabled': dates['disabled'],
                'extra': 0,
                'hold_button': hold_button,
                'tsErrorList': tsErrorList,
                'atErrorList': atErrorList,
                'tsFormList': tsContent,
                'atFormList': atContent}
        global dbSave
        if dbSave:
            getRelativeUrl = request.META['HTTP_REFERER']
            getRelativeUrl = getRelativeUrl.split("/")[3:]
            getRelativeUrl = "/".join(i for i in getRelativeUrl)
            return HttpResponseRedirect('/' + getRelativeUrl)

        return renderTimesheet(request, data)
    else:
        # GET request
        # Switch dates back and forth
        dates = switchWeeks(request)

        # Getting Data for timesheet and activity
        tsDataList = getTSDataList(request, dates['start'], dates['end'])

        # Common values initialization
        extra = 0

        tsFormList, atFormList = [], []

        # Approved TS data
        if len(tsDataList['tsData']) and len(tsDataList['atData']):
            tsFormList = tsDataList['tsData']
            atFormList = tsDataList['atData']
        elif len(tsDataList['tsData']):
            tsFormList = tsDataList['tsData']
        elif len(tsDataList['atData']):
            defaulLocation = [{'location': request.user.employee.location.id}]
            atFormList = tsDataList['atData']

        # Fresh TS data
        else:
            extra = 1
            if hasattr(request.user, 'employee'):
                defaulLocation = [
                    {'location': request.user.employee.location.id}]
            else:
                defaulLocation = [{'location': None}]
            messages.success(request, 'Please enter your timesheet for \
                             this week')
            hold_button = False

        # Constructing status of timesheet

        approvedSet = set()
        holdSet = set()
        saveSet = set()
        sentBackSet = set()
        if len(tsFormList):
            for eachTS in tsFormList:
                tsObj = TimeSheetEntry.objects.get(pk=eachTS['tsId'])
                if eachTS['approved']:
                    approvedSet.add(tsObj.project.projectId)
                elif eachTS['hold']:
                    holdSet.add(tsObj.project.projectId)
                else:
                    sentBackSet.add(tsObj.project.projectId)
        else:
            tsFormList = defaulLocation

        hold_button = False
        if len(approvedSet) > 0:
            messages.success(
                request, 'Timesheet approved :' + str(list(approvedSet)))
            hold_button = True
        if len(holdSet) > 0:
            messages.info(
                request, 'Timesheet pending manager approval :' +
                str(list(holdSet)))
            hold_button = True
        if len(sentBackSet) > 0:
            messages.info(
                request, 'Timesheet you have to submit:' +
                str(list(sentBackSet)))
            hold_button = False

        data = {'weekstartDate': dates['start'],
                'weekendDate': dates['end'],
                'disabled': dates['disabled'],
                'extra': extra,
                'hold_button': hold_button,
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
        disabled = ''
    elif request.GET.get('week') == 'next':
        weekstartDate = datetime.strptime(
            request.GET.get('startdate'), '%d%m%Y'
        ).date() + timedelta(days=7)
        ansrEndDate = datetime.strptime(
            request.GET.get('endDate'), '%d%m%Y'
        ).date() + timedelta(days=7)
        if (datetime.now().date() - ansrEndDate).days < 0:
            disabled = 'next'
        else:
            disabled = ''
    elif request.GET.get('wkstart'):

        weekstartDate = datetime.strptime(request.GET.get('wkstart'), '%d%m%Y').date()
        ansrEndDate = datetime.strptime(request.GET.get('wkend'), '%d%m%Y').date()
        if (datetime.now().date() - ansrEndDate).days < 0:
            disabled = 'next'
        else:
            disabled = ''


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


    mondays_list = [x for x in get_mondays_list_till_date()]

    # list of dict with mentioned ts entry columns
    weeks_timesheetEntry_list = TimeSheetEntry.objects.filter(teamMember=request.user, wkstart__in=mondays_list). \
        values('wkstart', 'wkend', 'hold', 'approved').distinct()

    mondays_list = [str(x.strftime("%b") + "-" + str(x.day)) for x in mondays_list]

    weeks_list = [x for x in weeks_list_till_date()]

    ts_week_info_dict = {}
    for dict_obj in weeks_timesheetEntry_list:
        for_week = str(str(dict_obj['wkstart'].day) + "-" + dict_obj['wkstart'].strftime("%b")) + " - "+ \
                   str(str(dict_obj['wkend'].day) + "-" + dict_obj['wkend'].strftime("%b"))
        dict_obj['for_week'] = for_week
        dict_obj['filled'] = True
        wkstart = str(dict_obj['wkstart']).split('-')[::-1]
        dict_obj['wkstart'] = "".join([x for x in wkstart])
        wkend = str(dict_obj['wkend']).split('-')[::-1]
        dict_obj['wkend'] = "".join([x for x in wkend])

        ts_week_info_dict[for_week] = dict_obj

    ts_final_list = []

    for tup in weeks_list:
        for_week = str(tup[0].day) + "-" + str(tup[0].strftime("%b")) + " - " + str(tup[1].day) + \
                    "-" + str(tup[1].strftime("%b"))
        if for_week in ts_week_info_dict:
            ts_final_list.append(ts_week_info_dict[for_week])
        else:
            wkstart = str(tup[0]).split('-')[::-1]
            wkend = str(tup[1]).split('-')[::-1]
            ts_final_list.append({'for_week':for_week, 'wkstart': "".join([x for x in wkstart]),
                                  'wkend': "".join([x for x in wkend]), 'filled': False})


    attendance = {}
    tsObj = TimeSheetEntry.objects.filter(
        wkstart=data['weekstartDate'],
        wkend=data['weekendDate'],
        teamMember=request.user,
    )
    billableHours = tsObj.filter(
        activity__isnull=True,
        task__taskType__in=['B','N']
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
    total = bTotal + idleTotal + othersTotal
    days = ['monday', 'tuesday', 'wednesday', 'thursday',
            'friday', 'saturday', 'sunday']
    d = {}
    for eachDay in days:
        newK = u'{0}Total'.format(eachDay)
        d[newK] = 0
        if 'atErrorList' not in data:
            if len(data['atFormList']):
                for eachData in data['atFormList']:
                    k = u'activity_{0}'.format(eachDay)
                    if k in eachData:
                        d[newK] += eachData[k]
        if 'tsErrorList' not in data:
            if len(data['tsFormList']):
                for eachData in data['tsFormList']:
                    k = u'{0}H'.format(eachDay)
                    if k in eachData:
                        d[newK] += eachData[k]
    endDate1=request.GET.get('enddate','')
    date=datetime.now().date()
    if request.GET.get("week")=='prev':
        endDate1=request.GET.get('enddate','')
        date=datetime.now().date()
        if endDate1:
            date = datetime(year=int(endDate1[4:8]), month=int(endDate1[2:4]), day=int(endDate1[0:2]))
            date -= timedelta(days=13)
        else:
            date=data['weekstartDate']

    elif request.GET.get("week")=='next':
        endDate1=request.GET.get('endDate','')
        date=datetime.now().date()
        if endDate1:
            date = datetime(year=int(endDate1[4:8]), month=int(endDate1[2:4]), day=int(endDate1[0:2]))
            date += timedelta(days=1)
        else:
            date=data['weekstartDate']

    else:
        date=data['weekstartDate']

    tsform = TimesheetFormset(request.user,date)
    if len(data['tsFormList']):
        tsFormset = formset_factory(tsform,
                                    extra=data['extra'],
                                    max_num=1,
                                    can_delete=True)
    else:
        tsFormset = formset_factory(tsform,
                                    extra=1,
                                    max_num=1,
                                    can_delete=True)
    if len(data['atFormList']):
        atFormset = formset_factory(ActivityForm,
                                    extra=data['extra'],
                                    max_num=1,
                                    can_delete=True)
    else:
        atFormset = formset_factory(ActivityForm,
                                    extra=1,
                                    max_num=1,
                                    can_delete=True)

    if len(data['tsFormList']) and len(data['atFormList']):
        atFormset = atFormset(initial=data['atFormList'], prefix='at')
        tsFormset = tsFormset(initial=data['tsFormList'])
    elif len(data['tsFormList']):
        tsFormset = tsFormset(initial=data['tsFormList'])
        atFormset = atFormset(prefix='at')
    elif len(data['atFormList']):
        atFormset = atFormset(initial=data['atFormList'], prefix='at')
    else:
        atFormset = atFormset(prefix='at')

    if hasattr(request.user, 'employee'):
        attendanceObj = employee.models.Attendance.objects.filter(
            employee=request.user.employee,
            attdate__range=[data['weekstartDate'], data['weekendDate']]
        )
        attendance = {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0}
        for eachObj in attendanceObj:
            if eachObj.swipe_out is not None or eachObj.swipe_in is not None:
                if eachObj.swipe_out is None:
                    timediff = eachObj.swipe_in
                    atttime = u"{0}:{1}".format(timediff.second // 3600,
                                                (timediff.second % 3600) // 60)
                elif eachObj.swipe_in is None:
                    timediff = eachObj.swipe_out
                    atttime = u"{0}:{1}".format(timediff.second // 3600,
                                                (timediff.second % 3600) // 60)
                else:
                    timediff = eachObj.swipe_out - eachObj.swipe_in
                    atttime = u"{0}:{1}".format(timediff.seconds // 3600,
                                                (timediff.seconds % 3600) // 60)
                attendance[u'{0}'.format(eachObj.attdate.weekday())] = atttime

        attendance = OrderedDict(sorted(attendance.items(), key=lambda t: t[0]))

    ocWeek = datetime.now().date() - data['weekstartDate']
    prevWeekBlock = False
    if ocWeek.days > 6:
        pwActivityData = TimeSheetEntry.objects.filter(
            Q(
                wkstart=data['weekstartDate'],
                wkend=data['weekendDate'],
                teamMember=request.user,
                project__isnull=True
            )
        ).values('approved', 'hold')
        if len(pwActivityData):
            if pwActivityData[0]['approved']:
                prevWeekBlock = True
            elif pwActivityData[0]['hold']:
                prevWeekBlock = True

    finalData = {'weekstartDate': data['weekstartDate'],
                 'weekendDate': data['weekendDate'],
                 'disabled': data['disabled'],
                 'shortDays': ['Mon', 'Tue', 'Wed', 'Thu',
                               'Fri', 'Sat', 'Sun'],
                 'hold_button': data['hold_button'],
                 'billableHours': billableHours,
                 'idleHours': idleHours,
                 'bTotal': bTotal,
                 'idleTotal': idleTotal,
                 'attendance': attendance,
                 'othersTotal': othersTotal,
                 'tsTotal': d,
                 'prevWeekBlock': prevWeekBlock,
                 'total': total,
                 'tsFormset': tsFormset,
                 'atFormset': atFormset,
                 'mondays_list': mondays_list,
                 'ts_week_info_dict': ts_week_info_dict,
                 'ts_final_list':ts_final_list
                 }
    if 'tsErrorList' in data:
        finalData['tsErrorList'] = data['tsErrorList']
    if 'atErrorList' in data:
        finalData['atErrorList'] = data['atErrorList']
    return render(request, 'MyANSRSource/timesheetEntry.html', finalData)


@login_required
@permission_required('MyANSRSource.approve_timesheet')
def ApproveTimesheet(request):
    if request.method == 'POST':
        for i in range(1, int(request.POST.get('totalValue')) + 1):
            choice = "choice" + str(i)
            mem = "mem" + str(i)
            start = "start" + str(i)
            end = "end" + str(i)
            fb = "fb" + str(i)
            if start in request.POST:
                startDate = date.fromordinal(int(request.POST.get(start)))
            if end in request.POST:
                endDate = date.fromordinal(int(request.POST.get(end)))
            if choice in request.POST:
                if request.POST.get(choice) != 'hold':
                    updateTS = TimeSheetEntry.objects.filter(
                        teamMember__id=int(request.POST.get(mem)),
                        wkstart=startDate,
                        wkend=endDate
                    )
                    for eachTS in updateTS:
                        if request.POST.get(choice) == 'redo':
                            eachTS.hold = False
                            eachTS.approved = False
                            eachTS.managerFeedback = request.POST.get(fb)
                        else:
                            eachTS.hold = True
                            eachTS.approved = True
                            eachTS.managerFeedback = request.POST.get(fb)
                        eachTS.save()
        return HttpResponseRedirect('/myansrsource/dashboard')
    else:
        data = TimeSheetEntry.objects.filter(
            project__projectmanager__user=request.user,
            hold=True, approved=False
        ).values('teamMember', 'teamMember__first_name',
                 'teamMember__id',
                 'teamMember__employee__employee_assigned_id',
                 'teamMember__last_name', 'wkstart', 'wkend'
                 ).order_by('teamMember', 'wkstart', 'wkend').distinct()

        tsList = []
        if len(data):
            for eachTS in data:
                tsData = {}
                tsData['member'] = eachTS['teamMember__first_name'] + ' :  ' + eachTS['teamMember__last_name'] + \
                    ' (' + eachTS['teamMember__employee__employee_assigned_id'] + ')'
                tsData['mem'] = eachTS['teamMember__id']
                tsData['wkstart'] = eachTS['wkstart']
                tsData['wkstartNum'] = eachTS['wkstart'].toordinal()
                tsData['wkend'] = eachTS['wkend']
                tsData['wkendNum'] = eachTS['wkend'].toordinal()
                totalNon = TimeSheetEntry.objects.filter(
                    wkstart=eachTS['wkstart'],
                    wkend=eachTS['wkend'],
                    teamMember=eachTS['teamMember'],
                    hold=True, approved=False,
                    project__isnull=True
                ).values('project').annotate(
                    monday=Sum('mondayH'),
                    tuesday=Sum('tuesdayH'),
                    wednesday=Sum('wednesdayH'),
                    thursday=Sum('thursdayH'),
                    friday=Sum('fridayH'),
                    saturday=Sum('saturdayH'),
                    sunday=Sum('sundayH')
                )
                tsData['NHours'] = sum(
                    [eachRec[eachDay] for eachDay in days for eachRec in totalNon])
                totalProjects = TimeSheetEntry.objects.filter(
                    wkstart=eachTS['wkstart'],
                    wkend=eachTS['wkend'],
                    teamMember=eachTS['teamMember'],
                    hold=True,
                    approved=False,
                    project__isnull=False).values(
                    'project',
                    'project__projectId',
                    'project__name',
                    'exception').distinct()
                tsData['projects'] = []
                for eachProject in totalProjects:
                    project = {}
                    project['name'] = eachProject[
                        'project__projectId'] + ' :  ' + eachProject['project__name']
                    project['exception'] = eachProject['exception']
                    project['BHours'] = getHours(request, eachTS['wkstart'],
                                                 eachTS['wkend'],
                                                 eachTS['teamMember'],
                                                 eachProject['project'], 'B')
                    project['IHours'] = getHours(request, eachTS['wkstart'],
                                                 eachTS['wkend'],
                                                 eachTS['teamMember'],
                                                 eachProject['project'], 'I')
                    tsData['projects'].append(project)
                tsList.append(tsData)
        unTsData = {'timesheetInfo': tsList}
        return render(request, 'MyANSRSource/timesheetApprove.html', unTsData)


@login_required
def getHours(request, wstart, wend, mem, project, label):
    ts = TimeSheetEntry.objects.filter(
        wkstart=wstart, wkend=wend,
        teamMember=mem, project=project, task__taskType=label
    ).values('project').annotate(
        monday=Sum('mondayH'),
        tuesday=Sum('tuesdayH'),
        wednesday=Sum('wednesdayH'),
        thursday=Sum('thursdayH'),
        friday=Sum('fridayH'),
        saturday=Sum('saturdayH'),
        sunday=Sum('sundayH')
    )
    return sum([eachRec[eachDay] for eachDay in days for eachRec in ts])


@login_required
def Dashboard(request):

    todays_date = datetime.now().date()
    birthdays_list = Employee.objects.filter(date_of_birthO__day=todays_date.day, date_of_birthO__month=todays_date.month)
    if request.method == 'POST':
        myremainder = MyRemainderForm(request.POST)
        btg = BTGReportForm(request.POST)
        if myremainder.is_valid():
            remaind = Remainder()
            remaind.name = myremainder.cleaned_data['name']
            remaind.startDate = myremainder.cleaned_data['startDate']
            remaind.endDate = myremainder.cleaned_data['endDate']
            remaind.user = request.user.employee
            remaind.save()
        if btg.is_valid():
            updateBtg = BTGReport()
            updateBtg.project = btg.cleaned_data['project']
            updateBtg.btg = btg.cleaned_data['btg']
            updateBtg.btgDate = datetime.now().date()
            updateBtg.member = request.user
            updateBtg.save()
    remainder = MyRemainderForm()
    #btg = BTGReportForm()
    if hasattr(request.user, 'employee'):
        myRemainders = Remainder.objects.filter(
            user=request.user.employee
        ).values('name', 'startDate', 'endDate', 'id')
    else:
        myRemainders = []
    if len(myRemainders):
        for eachRem in myRemainders:
            eachRem['startDate'] = eachRem[
                'startDate'
            ].strftime('%Y-%m-%d')
            eachRem['endDate'] = eachRem[
                'endDate'
            ].strftime('%Y-%m-%d')
            eachRem['del'] = eachRem['id']
    totalActiveProjects = Project.objects.filter(
        projectManager=request.user,
        closed=False
    ).count() if request.user.has_perm('MyANSRSource.manage_project') else 0

    myProjects = Project.objects.filter(
        projectManager=request.user,
    ).count() if request.user.has_perm('MyANSRSource.manage_project') else 0

    totalCurrentProjects = ProjectTeamMember.objects.filter(
        member=request.user,
        member__is_active=True,
        project__closed=False
    ).count()

    hract = HRActivity.objects.all().values('name', 'date')
    if len(hract):
        for eachAct in hract:
            eachAct['date'] = eachAct[
                'date'
            ].strftime('%Y-%m-%d')

    unApprovedTimeSheet = TimeSheetEntry.objects.filter(
        project__projectManager=request.user,
        approved=False, hold=True,
        teamMember__is_active=True
    ).count() if request.user.has_perm('MyANSRSource.approve_timesheet') else 0

    totalEmployees = User.objects.filter(is_active=True).count()
    pm = ProjectMilestone.objects.filter(
        project__projectManager=request.user,
        project__closed=False,
        closed=False
    )

    activeMilestones = pm.count() if request.user.has_perm(
        'MyANSRSource.manage_milestones') else 0

    financialM = pm.filter(
        financial=True).values(
        'description',
        'milestoneDate')
    nonfinancialM = pm.filter(
        financial=False).values(
        'description',
        'milestoneDate')

    for eachRec in financialM:
        eachRec['milestoneDate'] = eachRec['milestoneDate'].strftime('%Y-%m-%d')
    for eachRec in nonfinancialM:
        eachRec['milestoneDate'] = eachRec['milestoneDate'].strftime('%Y-%m-%d')

    tsProjectsCount = Project.objects.filter(
        closed=False,
        endDate__gte=datetime.now().date(),
        id__in=ProjectTeamMember.objects.filter(
            Q(member=request.user) |
            Q(project__projectManager=request.user)
        ).values('project_id')
    )
    TSProjectsCount = len(tsProjectsCount)

    billableProjects = ProjectTeamMember.objects.filter(
        project__closed=False,
        member=request.user,
        member__is_active=True,
        project__internal=False
    ).count()
    currentProjects = ProjectTeamMember.objects.filter(
        project__closed=False,
        member=request.user,
        member__is_active=True,
        project__startDate__lte=datetime.now(),
        project__endDate__gte=datetime.now()
    ).values('project__name', 'project__endDate')
    futureProjects = ProjectTeamMember.objects.filter(
        project__closed=False,
        member=request.user,
        member__is_active=True,
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
        member=request.user,
        member__is_active=True,
    ).values('project__name', 'project__startDate', 'project__endDate')
    for eachProject in myprojects:
        eachProject['project__startDate'] = eachProject[
            'project__startDate'
        ].strftime('%Y-%m-%d')
        eachProject['project__endDate'] = eachProject[
            'project__endDate'
        ].strftime('%Y-%m-%d')
    trainings = CompanyMaster.models.Training.objects.all().values(
        'batch', 'exercise', 'trainingDate', 'endDate')
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
    today = datetime.now().date()
    weekstartDate = today - timedelta(days=datetime.now().date().weekday())
    ansrEndDate = weekstartDate + timedelta(days=4)
    workingHours = 40
    if hasattr(request.user, 'employee'):
        locationId = request.user.employee.location
        weekHolidays = Holiday.objects.filter(
            location=locationId,
            date__range=[weekstartDate, ansrEndDate]
        ).values('date')
        if len(weekHolidays):
            workingHours = 40 - len(weekHolidays) * 8
    cp = ProjectTeamMember.objects.filter(
        member=request.user,
        #project__closed=False
        project__endDate__gte=today
    ).values(
        'project__projectId',
        'project__name',
        'project__book__name',
        'project__book__edition',
        'startDate',
        'endDate',
        'plannedEffort'
    )

    currYear=today.year
    currMonth=today.month
    currDay=today.day
    eddte=datetime(int(currYear),int(currMonth),int(currDay))
    attendenceDetail=employee.models.Attendance.objects.filter(
     attdate__lte=eddte,
     employee_id__user_id=request.user.id).values('swipe_in','swipe_out','attdate').filter(Q(swipe_in__isnull=False) & Q(swipe_out__isnull=False) & Q(attdate__isnull=False))#.exclude(swipe_in="", swipe_out="", attdate="")
    swipe_display=[]
    
    
    for val in attendenceDetail:
        temp={}
        temp['date']=val['attdate'].strftime('%Y-%m-%d')
        temp['swipe_in']=val['swipe_in']
        temp['swipe_out']=val['swipe_out']
        swipe_display.append(temp)
    eachProjectHours = 0
    if len(cp):
        eachProjectHours = workingHours / len(cp)
    myReq = Respondent.objects.filter(
        employee=request.user,
        status='P',
    )
    myPeerReqCount = len(myReq)
    myReportee = employee.models.Employee.objects.filter(
        manager=request.user.employee)
    isManager = 0
    if myReportee:
        isManager = 1
    data = {
        'username': request.user.username,
        'firstname': request.user.first_name,
        'cp': cp,
        'eachProjectHours': eachProjectHours,
        'workingHours': workingHours,
        'TSProjectsCount': TSProjectsCount,
        'holidayList': holidayList,
        'projectsList': myprojects,
        'trainingList': trainings,
        'hrList': hract,
        'remainders': myRemainders,
        'financialM': financialM,
        'nonfinancialM': nonfinancialM,
        'billableProjects': billableProjects,
        'myProjects': myProjects,
        'currentProjects': currentProjects,
        'remainderForm': remainder,
        'futureProjects': futureProjects,
        'activeProjects': totalActiveProjects,
        'activeMilestones': activeMilestones,
        'unapprovedts': unApprovedTimeSheet,
        'myPeerReqCount': myPeerReqCount,
        'totalemp': totalEmployees,
        'isManager': isManager,
        'swipe_display': swipe_display,
        'birthdays_list': birthdays_list,
    }
    # the following added for grievance administration module
    if request.user.groups.filter(name='myansrsourceGrievanceAdmin').exists():
        grievances_count = Grievances.objects.all().count()
        data['grievances_count'] = grievances_count

    return render(request, 'MyANSRSource/landingPage.html', data)


def checkUser(userName, password, request, form):
    try:
        user = authenticate(username=userName, password=password)
        if user is not None:
            if user.is_active:
                if hasattr(user, 'employee'):
                    if user.has_perm('MyANSRSource.enter_timesheet'):
                        auth.login(request, user)
                        return HttpResponseRedirect('/myansrsource/dashboard')
                    else:
                        # We have an unknow group
                        logger.error(
                            u'User {0} permission details {1} group perms'.format(
                                user.username,
                                user.get_all_permissions(),
                                user.get_group_permissions()))
                        senderEmail = settings.NEW_JOINEE_NOTIFIERS
                        context = {'username': user.username}
                        for eachRecp in senderEmail:
                            SendMail(context, eachRecp, 'newjoinee')
                        return render(request, 'MyANSRSource/welcome.html', {})
                else:
                    logger.error(
                        u'User {0} has no employee data'.format(
                            user.username)
                    )
                    senderEmail = settings.NEW_JOINEE_NOTIFIERS
                    context = {'username': user.username}
                    for eachRecp in senderEmail:
                        SendMail(context, eachRecp, 'newjoinee')
                    return render(request, 'MyANSRSource/welcome.html', {})
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


class ManageTeamLeaderWizard(SessionWizardView):

    def get_template_names(self):
        return [TLTEMPLATES[self.steps.current]]

    def get_form(self, step=None, data=None, files=None):
        form = super(ManageTeamLeaderWizard, self).get_form(step, data, files)
        step = step if step else self.steps.current
        if step == 'My Projects':
            projects = Project.objects.filter(projectManager=self.request.user,
                                              closed=False)
            form.fields['project'].queryset = projects
        return form

    def get_form_initial(self, step):
        projectMS = {}
        if step == 'Manage Project Leader':
            myProject = self.get_cleaned_data_for_step('My Projects')['project']
            pm = Project.objects.filter(id=myProject.id).values(
                'projectManager',
            )
            l = []
            for eachData in pm:
                l.append(eachData['projectManager'])
            projectMS = {'projectManager': l}
            return self.initial_dict.get(step, projectMS)

    def done(self, form_list, **kwargs):
        updatedData = [form.cleaned_data for form in form_list][
            1]['projectManager']
        myProject = self.get_cleaned_data_for_step('My Projects')['project']
        myProject = Project.objects.get(id=myProject.id)
        allData = ProjectManager.objects.filter(
            project=myProject).values('id', 'user')
        updateDataId = [eachData.id for eachData in updatedData]
        for eachData in allData:
            if eachData['user'] not in updateDataId:
                ProjectManager.objects.get(pk=eachData['id']).delete()
        for eachData in updatedData:
            pm = ProjectManager()
            oldData = ProjectManager.objects.filter(
                project=myProject, user=eachData).values('id')
            if len(oldData):
                pass
            else:
                pm.project = myProject
                pm.user = eachData
                pm.save()
        return HttpResponseRedirect('/myansrsource/dashboard')

manageTeamLeader = ManageTeamLeaderWizard.as_view(TLFORMS)


@login_required
@permission_required('MyANSRSource.manage_project')
def WrappedManageTeamLeaderView(request):
    return manageTeamLeader(request)


class TrackMilestoneWizard(SessionWizardView):

    def get_template_names(self):
        return [TMTEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super(TrackMilestoneWizard, self).get_context_data(
            form=form, **kwargs)
        if self.steps.current == 'Manage Milestones':
            selectedProjectId = self.storage.get_step_data(
                'My Projects'
            )['My Projects-project']
            projectObj = Project.objects.get(pk=selectedProjectId)
            totalValue = projectObj.totalValue
            projectType = projectObj.internal
            context.update({'totalValue': totalValue, 'type': projectType})
        return context

    def get_form(self, step=None, data=None, files=None):
        form = super(TrackMilestoneWizard, self).get_form(step, data, files)
        step = step if step else self.steps.current
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

                if form.is_valid():
                    selectedProjectId = self.storage.get_step_data(
                        'My Projects'
                    )['My Projects-project']
                    projectObj = Project.objects.get(pk=selectedProjectId)
                    projectTotal = projectObj.totalValue
                    totalRate = 0
                    for eachForm in form:
                        if eachForm.is_valid():
                            totalRate += eachForm.cleaned_data['amount']
                            if eachForm.cleaned_data['financial'] is False:
                                if eachForm.cleaned_data['amount'] > 0:
                                    amount = eachForm.cleaned_data['amount']
                                    errors = eachForm._errors.setdefault(
                                        amount, ErrorList())
                                    errors.append(u'Please select milestone as \
                                                  financial')
                            elif eachForm.cleaned_data['amount'] == 0:
                                amount = eachForm.cleaned_data['amount']
                                errors = eachForm._errors.setdefault(
                                    amount, ErrorList())
                                errors.append(u'Financial Milestone amount \
                                            cannot be 0')
                    if float(projectTotal) != float(totalRate):
                        errors = eachForm._errors.setdefault(
                            totalRate, ErrorList())
                        errors.append(u'Total amount must be \
                                    equal to project value')
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
@permission_required('MyANSRSource.manage_milestones')
def WrappedTrackMilestoneView(request):
    return TrackMilestone(request)


class ChangeProjectWizard(SessionWizardView):

    def get_template_names(self):
        return [CTEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super(ChangeProjectWizard, self).get_context_data(
            form=form, **kwargs)
        if self.steps.current == 'Change Basic Information':
            currentProject = Project.objects.filter(
                pk=self.storage.get_step_data(
                    'My Projects'
                )['My Projects-project']).values(
                'plannedEffort',
                'name',
                'projectId'
                )[0]
            totalEffort = currentProject['plannedEffort']
            projectName = u"{1} : {0}".format(currentProject['name'],
                                              currentProject['projectId'])
            context.update({'totalEffort': totalEffort,
                            'projectName': projectName})
        return context

    def get_form(self, step=None, data=None, files=None):
        form = super(ChangeProjectWizard, self).get_form(step, data, files)
        step = step if step else self.steps.current
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
        return form

    def get_form_initial(self, step):
        currentProject = []
        if step == 'Change Basic Information':
            projectId = self.storage.get_step_data(
                'My Projects'
            )['My Projects-project']
            if projectId is not None:
                currentProject = Project.objects.filter(
                    pk=projectId).values(
                    'id',
                    'signed',
                    'endDate',
                    'plannedEffort',
                    'totalValue',
                    'salesForceNumber',
                    'po'
                    )[0]
                currentProject['revisedTotal'] = currentProject['totalValue']
                currentProject['revisedEffort'] = currentProject[
                    'plannedEffort']
        return self.initial_dict.get(step, currentProject)

    def done(self, form_list, **kwargs):
        data = UpdateProjectInfo(
            self.request, [
                form.cleaned_data for form in form_list])
        return render(
            self.request,
            'MyANSRSource/changeProjectId.html',
            data)


def UpdateProjectInfo(request, newInfo):
    """
        newInfo[0] ==> Selected Project Object
        newInfo[1] ==> 'reason' , 'endDate', 'revisedEffort', 'revisedTotal',
                       'closed', 'signed'
    """
    try:
        pru = newInfo[0]['project']
        pru.plannedEffort = newInfo[1]['revisedEffort']
        pru.totalValue = newInfo[1]['revisedTotal']
        pru.closed = newInfo[1]['closed']
        pru.signed = newInfo[1]['signed']
        pru.po = newInfo[1]['po']
        pru.endDate = newInfo[1]['endDate']
        pru.salesForceNumber = newInfo[1]['salesForceNumber']
        pru.save()

        pci = ProjectChangeInfo()
        pci.project = pru
        pci.reason = newInfo[1]['reason']
        pci.endDate = newInfo[1]['endDate']
        pci.salesForceNumber = newInfo[1]['salesForceNumber']
        pci.revisedEffort = newInfo[1]['revisedEffort']
        pci.revisedTotal = newInfo[1]['revisedTotal']
        pci.closed = newInfo[1]['closed']
        if pci.closed is True:
            pci.closedOn = datetime.now().replace(tzinfo=utc)
        pci.signed = newInfo[1]['signed']
        pci.save()

        # We need the Primary key to create the CRId
        pci.crId = u"CR-{0}".format(pci.id)
        pci.save()

        return {'crId': pci.crId}
    except (ProjectTeamMember.DoesNotExist,
            ProjectMilestone.DoesNotExist) as e:
        messages.error(request, 'Could not save change request information')
        logger.error('Exception in UpdateProjectInfo :' + str(e))
        return {'crId': None}

changeProject = ChangeProjectWizard.as_view(CFORMS)


@login_required
@permission_required('MyANSRSource.manage_project')
def WrappedChangeProjectView(request):
    return changeProject(request)


class CreateProjectWizard(SessionWizardView):

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_form(self, step=None, data=None, files=None):
        form = super(CreateProjectWizard, self).get_form(step, data, files)
        step = step if step else self.steps.current
        if step == 'Basic Information':
            if self.get_cleaned_data_for_step('Define Project') is not None:
                signed = self.get_cleaned_data_for_step(
                    'Define Project')['signed']
                if signed is not None:
                    if signed == 'False':
                        form.fields['po'].widget.attrs[
                            'readonly'
                        ] = 'True'
                else:
                    logger.error("Basic Information step has signed as none")
                if form.is_valid():
                    self.request.session['PStartDate'] = form.cleaned_data[
                        'startDate'
                    ].strftime('%Y-%m-%d')
                    self.request.session['PEndDate'] = form.cleaned_data[
                        'endDate'
                    ].strftime('%Y-%m-%d')
            else:
                logger.error(
                    "Basic Information step data is None" + str(form._errors))

        if step == 'Financial Milestones':
            defineProject = self.get_cleaned_data_for_step('Define Project')
            if defineProject is not None:
                internalStatus = defineProject['internal']
                for eachForm in form:
                    eachForm.fields['DELETE'].widget.attrs[
                        'disabled'
                    ] = 'True'
                    eachForm.fields['DELETE'].widget.attrs[
                        'class'
                    ] = 'form-control'
                if internalStatus is not None:
                    if internalStatus == 'True':
                        for eachForm in form:
                            eachForm.fields['financial'].widget.attrs[
                                'disabled'
                            ] = 'True'
                            eachForm.fields['amount'].widget.attrs[
                                'readonly'
                            ] = 'True'
                    else:
                        if form.is_valid():
                            if self.get_cleaned_data_for_step('Basic Information') is not None:
                                projectTotal = self.get_cleaned_data_for_step(
                                    'Basic Information')['totalValue']
                                totalRate = 0
                                for eachForm in form:
                                    if eachForm.is_valid():
                                        totalRate += eachForm.cleaned_data['amount']
                                        if eachForm.cleaned_data['financial'] is False:
                                            if eachForm.cleaned_data['amount'] > 0:
                                                amount = eachForm.cleaned_data[
                                                    'amount']
                                                errors = eachForm._errors.setdefault(
                                                    amount,
                                                    ErrorList())
                                                errors.append(u'Please select milestone as \
                                                            financial')
                                        elif eachForm.cleaned_data['amount'] == 0:
                                            amount = eachForm.cleaned_data[
                                                'amount']
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
                            else:
                                logger.error(
                                    "Financial Milestone step has totalValue as none" + str(form._errors))
                else:
                    logger.error(
                        "Financial Milestone step has internal as none" +
                        str(form._errors))
            else:
                logger.error(
                    "Financial Milestone step has step data as none" +
                    str(form._errors))
        return form

    def get_context_data(self, form, **kwargs):
        context = super(CreateProjectWizard, self).get_context_data(
            form=form, **kwargs)
        if self.steps.current == 'Basic Information':
            if self.get_cleaned_data_for_step('Define Project') is not None:
                pt = self.get_cleaned_data_for_step(
                    'Define Project')['projectType']
                data = {'pt': projectType.objects.get(id=pt.id).description}
            else:
                logger.error(
                    "Basic Information step has project as none" +
                    str(form._errors))
                data = {}
            context.update(data)

        if self.steps.current == 'Financial Milestones':
            if self.get_cleaned_data_for_step('Basic Information') is not None:
                projectTotal = self.get_cleaned_data_for_step(
                    'Basic Information')['totalValue']
            else:
                logger.error(
                    "Financial step has project as none" + str(form._errors))
                data = {}
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
                    project__id=projectId,
                    active=True).values('id', 'member',
                                        'startDate', 'endDate',
                                        'datapoint',
                                        'plannedEffort', 'rate'
                                        )
            else:
                logger.error(u"Project Id : {0}, Request: {1},".format(
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

    def get_form(self, step=None, data=None, files=None):
        form = super(ManageTeamWizard, self).get_form(step, data, files)
        step = step if step else self.steps.current
        if step == 'Manage Team':
            selectedProjectId = self.storage.get_step_data(
                'My Projects'
            )['My Projects-project']
            projectObj = Project.objects.get(pk=selectedProjectId)
            predicted = projectObj.plannedEffort
            actual = 0
            for eachForm in form:
                if eachForm.is_valid():
                    if eachForm.cleaned_data['plannedEffort'] is None:
                        actual += 0
                    else:
                        actual += eachForm.cleaned_data['plannedEffort']
            if actual > predicted:
                for eachForm in form:
                    errors = eachForm._errors.setdefault(
                        actual, ErrorList())
                    errors.append(u'Total planned effort is more than \
                                  project total effort')
        return form

    def done(self, form_list, **kwargs):
        project = [form.cleaned_data for form in form_list][0]['project']
        cleanList = [form.cleaned_data for form in form_list][1]
        for eachData in cleanList:
            if eachData['plannedEffort'] is None:
                eachData['plannedEffort'] = 0
            if eachData['member'] is None:
                pass
            else:
                if eachData['id']:
                    if eachData['DELETE']:
                        ptm = ProjectTeamMember.objects.get(
                            pk=eachData['id'])
                        NotifyMember(ptm.id, True)
                        ptm.active = False
                        ptm.save()
                    else:
                        ptm = ProjectTeamMember.objects.get(pk=eachData['id'])
                        if (eachData['startDate'] == ptm.startDate) and \
                           (eachData['endDate'] == ptm.endDate) and \
                           (eachData['plannedEffort'] == ptm.plannedEffort) and \
                           (eachData['member'] == ptm.member) and \
                           (eachData['datapoint'] == ptm.datapoint) and \
                                (eachData['rate'] == ptm.rate):
                            pass
                        else:
                            ptm.project = project
                            del(eachData['id'])
                            for k, v in eachData.iteritems():
                                setattr(ptm, k, v)
                            ptm.save()
                            NotifyMember(ptm.id, False)
                else:
                    ptm = ProjectTeamMember()
                    ptm.project = project
                    del(eachData['id'])
                    for k, v in eachData.iteritems():
                        setattr(ptm, k, v)
                    ptm.save()
                    NotifyMember(ptm.id, False)
        return HttpResponseRedirect('/myansrsource/dashboard')


manageTeam = ManageTeamWizard.as_view(MEMBERFORMS)


@login_required
@permission_required('MyANSRSource.manage_project')
def WrappedManageTeamView(request):
    return manageTeam(request)


def NotifyMember(ptmid, delete):
    teamMember = ProjectTeamMember.objects.get(pk=ptmid)
    email = teamMember.member.email
    if delete:
        if len(email) > 0:
            context = {
                'first_name': teamMember.member.first_name,
                'projectId': teamMember.project.projectId,
                'projectName': teamMember.project.name,
                'startDate': teamMember.project.startDate,
                'mystartdate': teamMember.startDate,
            }
            SendMail(context, email, 'projectRemovedTeam')
    else:
        pm = ProjectManager.objects.filter(
            project=teamMember.project
        ).values('user__first_name', 'user__last_name')
        l = []
        for eachManager in pm:
            name = eachManager['user__first_name'] + \
                "  " + eachManager['user__last_name']
            l.append(name)
        if len(l) > 1:
            manager = ",".join(l)
        else:
            manager = "  ".join(l)
        if email != '':
            context = {
                'first_name': teamMember.member.first_name,
                'projectId': teamMember.project.projectId,
                'projectName': teamMember.project.name,
                'pmname': manager,
                'startDate': teamMember.project.startDate,
                'mystartdate': teamMember.startDate,
                'plannedEffort': teamMember.plannedEffort,
            }
            SendMail(context, email, 'projectCreatedTeam')


def SendMail(data, toAddr, templateName):
    sm = SendEmail()
    if 'startDate' in data:
        data['startDate'] = data['startDate'].strftime("%d-%m-%Y")
    if 'mystartdate' in data:
        data['mystartdate'] = data['mystartdate'].strftime("%d-%m-%Y")
    if 'plannedEffort' in data:
        data['plannedEffort'] = str(data['plannedEffort'])
    sm.content = json.dumps(data)
    sm.template_name = templateName
    sm.toAddr = json.dumps([toAddr])
    sm.save()


@login_required
@permission_required('MyANSRSource.create_project')
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
            startDate = datetime.fromtimestamp(
                int(request.POST.get('startDate'))).date()
            endDate = datetime.fromtimestamp(
                int(request.POST.get('endDate'))).date()
            pr.startDate = startDate
            pr.endDate = endDate
            pr.po = request.POST.get('po')
            pr.totalValue = float(request.POST.get('totalValue'))
            pr.plannedEffort = int(request.POST.get('plannedEffort'))
            pr.salesForceNumber = int(request.POST.get('salesForceNumber'))
            pr.currentProject = request.POST.get('currentProject')
            pr.signed = (request.POST.get('signed') == 'True')
            pr.bu = CompanyMaster.models.BusinessUnit.objects.get(
                pk=int(request.POST.get('bu'))
            )
            pr.customer = CompanyMaster.models.Customer.objects.get(
                pk=int(request.POST.get('customer'))
            )
            pr.internal = pr.customer.internal
            pr.customerContact = request.POST.get('customerContact')
            pr.book = Book.objects.get(
                pk=int(request.POST.get('book'))
            )

            projectIdPrefix = u"{0}-{1}-{2}".format(
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
            if request.user.id not in eval(request.POST.get('pm')):
                pm = ProjectManager()
                pm.user = request.user
                pm.project = pr
                pm.save()
            if pr.internal == False:
                context = {
                    'projectId': pr.projectId,
                    'projectName': pr.name,
                }
                senderEmail = settings.EXTERNAL_PROJECT_NOTIFIERS
                for eachRecp in senderEmail:
                    SendMail(context, eachRecp, 'externalproject')

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
@permission_required('MyANSRSource.create_project')
def WrappedCreateProjectView(request):
    return createProject(request)


@login_required
@permission_required('MyANSRSource.create_project')
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
        name = eachManager['user__first_name'] + \
            "  " + eachManager['user__last_name']
        l.append(name)
    if len(l) > 1:
        manager = ",".join(l)
    else:
        manager = "  ".join(l)
    projectHead = CompanyMaster.models.Customer.objects.filter(
        id=int(request.POST.get('customer')),
    ).values('Crelation__email',
             'Crelation__first_name',
             'Crelation__last_name')
    for eachHead in projectHead:
        if eachHead['Crelation__email'] != '':
            context = {
                'first_name': eachHead['Crelation__first_name'],
                'projectId': projectDetails.projectId,
                'projectName': projectName,
                'pmname': manager,
                'startDate': projectDetails.startDate
            }
            SendMail(context, eachHead['Crelation__email'],
                     'projectCreatedMgmt')
    data = {'projectCode': request.POST.get('projectCode'),
            'projectName': projectName,
            'notify': 'F'}
    return render(request, 'MyANSRSource/projectSuccess.html', data)


@login_required
def deleteProject(request):
    ProjectBasicInfoForm()
    return HttpResponseRedirect('add')


@login_required
@permission_required('MyANSRSource.create_project')
def ViewProject(request):
    if request.method == 'POST':
        projectId = int(request.POST.get('project'))
        projectObj = Project.objects.filter(id=projectId)
        basicInfo = projectObj.values(
            'projectType__description', 'bu__name', 'customer__name',
            'name', 'book__name', 'signed', 'internal', 'currentProject',
            'projectId', 'customerContact'
        )[0]
        if basicInfo['customerContact']:
            customerObj = basicInfo['customerContact']
            basicInfo['customerContact__username'] = customerObj
        flagData = projectObj.values(
            'startDate', 'endDate', 'plannedEffort', 'contingencyEffort',
            'totalValue', 'po', 'salesForceNumber'
        )[0]
        cleanedTeamData = ProjectTeamMember.objects.filter(
            project=projectObj).values(
            'member__username', 'startDate', 'endDate',
            'plannedEffort', 'rate'
            )
        if basicInfo['internal']:
            cleanedMilestoneData = []
        else:
            cleanedMilestoneData = ProjectMilestone.objects.filter(
                project=projectObj).values('milestoneDate', 'description',
                                           'amount', 'financial')

        changeTracker = ProjectChangeInfo.objects.filter(
            project=projectObj).values(
            'reason', 'endDate', 'revisedEffort', 'revisedTotal',
            'closed', 'closedOn', 'signed', 'salesForceNumber',
            'updatedOn'
        ).order_by('updatedOn')
        data = {
            'basicInfo': basicInfo,
            'flagData': flagData,
            'teamMember': cleanedTeamData,
            'milestone': cleanedMilestoneData,
            'changes': changeTracker,
            }
        if len(changeTracker):
            closedOn = [
                eachRec
                ['closedOn']
                for eachRec in changeTracker if eachRec['closedOn'] is not None]
            if len(closedOn):
                data['closedOn'] = closedOn[0].strftime("%B %d, %Y, %r")
        return render(request, 'MyANSRSource/viewProjectSummary.html', data)
    data = Project.objects.filter(projectManager=request.user).values(
        'name', 'id', 'closed', 'projectId'
    )
    return render(request, 'MyANSRSource/viewProject.html', {'projects': data})


def GetChapters(request, projectid):
    try:
        projectObj = Project.objects.get(pk=projectid)
        chapters = Chapter.objects.filter(
            book=projectObj.book).values(
            'id',
            'name')
        json_chapters = {'data': list(chapters)}
    except Project.DoesNotExist:
        json_chapters = {'data': list()}
    return HttpResponse(json.dumps(json_chapters),
                        content_type="application/javascript")


def GetTasks(request, projectid):
    try:
        tasks = Task.objects.filter(
            projectType=Project.objects.get(pk=projectid).projectType,
            active=True
        ).values('code', 'name', 'id', 'taskType', 'norm')
        for eachRec in tasks:
            eachRec['norm'] = float(eachRec['norm'])
        a1=request.GET.get('endDate')
        date = datetime(year=int(a1[4:8]), month=int(a1[2:4]), day=int(a1[0:2])).date()
        pEndDate=Project.objects.get(pk=projectid).endDate
        diff=date-pEndDate
        diff=diff.days
        if diff<0:
            diff=0
        data = {'data': list(tasks), 'flag':diff}
    except Task.DoesNotExist:
        diff=0
        data = {'data': list(), 'flag':diff}
    return HttpResponse(json.dumps(data), content_type="application/json")

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
    return HttpResponse(json.dumps(data), content_type="application/json")


def GetProjectType(request):
    try:
        strtDate1=request.GET.get('strtDate')
        date1 = datetime(year=int(strtDate1[4:8]), month=int(strtDate1[2:4]), day=int(strtDate1[0:2])).date()
        typeData = ProjectTeamMember.objects.values(
            'project__id',
            'project__name',
            'project__projectType__code',
            'project__projectType__description'
        ).filter(project__endDate__gte=date1
        #project__closed=False
        )
        data = {'data': list(typeData)}
    except ProjectTeamMember.DoesNotExist:
        data = {'data': list()}
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type="application/json")


def DeleteRemainder(request, remid):
    if remid:
        rem = Remainder.objects.get(pk=remid)
        try:
            rem.delete()
            return HttpResponse({'data': 'S'}, content_type="application/json")
        except:
            return HttpResponse({'data': ''}, content_type="application/json")


def csrf_failure(request, reason=""):
    return render(request, 'MyANSRSource/csrfFailure.html', {'reason': reason})


def Logout(request):
    logout(request)
    request.session.flush()
    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
    return HttpResponseRedirect('/myansrsource')
