import logging

import json
import CompanyMaster
import employee
import os
import xlsxwriter
from decimal import Decimal
from collections import OrderedDict
from django.contrib.auth.decorators import permission_required

from django.forms.utils import ErrorList
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.contrib import auth, messages
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse ,JsonResponse
from formtools.wizard.views import SessionWizardView
from django.forms.formsets import formset_factory
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime, timedelta, date
from django.db.models import Q, Sum
from django.utils.timezone import utc
from django.conf import settings
from employee.models import Employee, Remainder, EmployeeArchive
from Leave.views import leavecheck, daterange
from django.views.generic import View, TemplateView
from django.core.exceptions import PermissionDenied
from tasks import TimeSheetWeeklyReminder, TimeSheetRejectionNotification, ProjectChangeRejection, ProjectRejection
from fb360.models import Respondent
from reportviews import *
from MyANSRSource.models import Project, TimeSheetEntry, \
    ProjectMilestone, Milestone,  ProjectTeamMember, Book, ProjectChangeInfo, \
    Chapter, projectType, Task, ProjectManager, SendEmail, BTGReport, \
    ProjectDetail, qualitysop, ProjectScope, ProjectAsset, Milestone, change_file_path,ProjectSopTemplate

from MyANSRSource.forms import LoginForm, ProjectBasicInfoForm, \
    ActivityForm, TimesheetFormset, ProjectFlagForm, \
    ChangeProjectBasicInfoForm, ChangeProjectTeamMemberForm, \
    MyRemainderForm, ChangeProjectForm, CloseProjectMilestoneForm, \
    changeProjectLeaderForm, BTGReportForm, UploadForm, RejectProjectForm, ModifyProjectInfoForm, CloseProjectMilestoneFormDelivery

from CompanyMaster.models import Holiday, HRActivity, Practice, SubPractice
from Grievances.models import Grievances
from QMS.models import TemplateMaster, QMSProcessModel,ProjectTemplateProcessModel, TemplateProcessReview
from ldap import LDAPError
logger = logging.getLogger('MyANSRSource')
# views for ansr

FORMS = [
    ("Define Project", ProjectBasicInfoForm),
    ("Basic Information", ProjectFlagForm),
    ("Uploads",  UploadForm)
]
TEMPLATES = {
    "Define Project": "MyANSRSource/projectDefinition.html",
    "Basic Information": "MyANSRSource/projectBasicInfo.html",
    "Uploads": "MyANSRSource/ProjectUploads.html",
}

CFORMS = [
    ("My Projects", ChangeProjectForm),
    ("Change Basic Information", ChangeProjectBasicInfoForm),
]

MFORMS = [
    ("Rejected Projects", RejectProjectForm),
    ("Modify Basic Information", ModifyProjectInfoForm),
]

CTEMPLATES = {
    "My Projects": "MyANSRSource/changeProject.html",
    "Change Basic Information": "MyANSRSource/changeProjectBasicInfo.html",
}

MTEMPLATES = {
    "Rejected Projects": "MyANSRSource/modifyProject.html",
    "Modify Basic Information": "MyANSRSource/modifyProjectBasicInfo.html",
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

TMFORMSDELIVERY = [
    ("My Projects", ChangeProjectForm),
    ("Manage Milestones", formset_factory(
        CloseProjectMilestoneFormDelivery,
        extra=1,
        max_num=1,
        can_delete=True
    )),
]

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

def getheadid(request):
    practicename = request.GET['practicename']
    practice = Practice.objects.select_related('head').get(id=practicename)
    return HttpResponse(practice.head.first_name + " " + practice.head.last_name)


def soplink(request):
    sopid = request.GET['sop']
    soplink  = qualitysop.objects.get(id=sopid)
    request.session['sop_name'] = soplink.name
    data = json.dumps({
        'actions': soplink.SOPlink,
    })
    return HttpResponse(data, content_type='application/json')


def milestonename(request):
    type_id = request.GET['milestone_type_id']
    name = Milestone.objects.get(id=type_id).milestone_type
    return HttpResponse(name)

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


previous_year_month = [10, 11, 12]


def get_mondays_list_till_date():
    '''generate all days that are Mondays in the current year
    returns only monday(date object)'''
    current_date = datetime.now().date()
    jan1 = date(current_date.year, 1, 1)
    jan1 = date(current_date.year - 1, 10, 1)  # to shows last 3 months from previous year

    # find first Monday (which could be this day)
    monday = jan1 + timedelta(days=(7 - jan1.weekday()) % 7)

    while 1:

        if (monday.year != current_date.year and monday.month not in previous_year_month) or monday > current_date:
            break
        yield monday
        monday += timedelta(days=7)


# diff between above function get_mondays_list_till_date() and below function weeks_list_till_date
# is only in the yield statement
#
def weeks_list_till_date(ignore_last_year=True):
    '''generate week(monday to sunday) for the current year
    returns tuple for with 2 objects: week_start and week_end'''
    current_date = datetime.now().date()
    if ignore_last_year:
        jan1 = date(current_date.year, 1, 1)
    else:
        jan1 = date(current_date.year - 1, 10, 1)

    # find first Monday (which could be this day)
    monday = jan1 + timedelta(days=(7 - jan1.weekday()) % 7)

    while 1:
        if ignore_last_year:
            if monday.year != current_date.year or monday > current_date:
                break
        else:
            if (monday.year != current_date.year and monday.month not in previous_year_month) or monday > current_date:
                break
        yield (monday, monday + timedelta(days=6))
        monday += timedelta(days=7)


# to convert unicode strings to string with apostrophe removed from each project name
def unicode_to_string(resultant_set):
    return str([x.encode('UTF8') for x in resultant_set]).replace("'", "")


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
        else:
            startdate = request.GET.get('startdate', '')
            if startdate:
                tmp_date = datetime(year=int(startdate[4:8]), month=int(startdate[2:4]), day=int(startdate[0:2]))
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
                weekTotalValidate = 40 - ((8 * len(weekHolidays)) +
                                          int(pull_members_week(request, changedStartDate, changedEndDate)))
                weekTotalValidate = float(weekTotalValidate)
                weekTotalExtra = weekTotalValidate + 4
            else:
                weekHolidays = []
                weekTotalValidate = 40
                weekTotalExtra = 4

            # condition to stop users from deleting all projects and submit time sheet
            delete_count = 0
            ts_id_count = 0
            if 'save' not in request.POST:
                for time_sheet in timesheets:
                    if time_sheet.cleaned_data['tsId']:
                        ts_id_count += 1
                    if time_sheet.cleaned_data['DELETE'] is True:
                        delete_count += 1
                if ts_id_count == delete_count and ts_id_count == delete_count != 0:
                    messages.error(request, "You Can't Submit Your Time Sheet Without Entering Details For Project")
                    data = get_time_sheet(request)
                    return renderTimesheet(request, data)  # condition ends here

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
                    del (timesheet.cleaned_data['DELETE'])
                    del (timesheet.cleaned_data['monday'])
                    del (timesheet.cleaned_data['tuesday'])
                    del (timesheet.cleaned_data['wednesday'])
                    del (timesheet.cleaned_data['thursday'])
                    del (timesheet.cleaned_data['friday'])
                    del (timesheet.cleaned_data['saturday'])
                    del (timesheet.cleaned_data['sunday'])
                    del (timesheet.cleaned_data['total'])
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
            if (mondayTotal > 24) | (tuesdayTotal > 24) | \
                    (wednesdayTotal > 24) | (thursdayTotal > 24) | \
                    (fridayTotal > 24) | (saturdayTotal > 24) | \
                    (sundayTotal > 24):
                messages.error(request, 'You can only work for 24 hours a day')
            for activity in activities:
                if activity.cleaned_data['activity'] is not None:
                    if activity.cleaned_data['DELETE'] is True:
                        TimeSheetEntry.objects.filter(
                            id=activity.cleaned_data['atId']
                        ).delete()
                    else:
                        del (activity.cleaned_data['DELETE'])
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
                        weekTotal < weekTotalValidate - 0.05):
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
                            elif k == 'remarks':
                                nonbillableTS.remarks = v
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
                            if k in (
                            'mondayH', 'tuesdayH', 'wednesdayH', 'thursdayH', 'fridayH', 'saturdayH', 'sundayH'):
                                if v is None:
                                    v = float(0.0)
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
                            # nonbillableTS.approved = True
                            # nonbillableTS.managerFeedback = 'System Approved'
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
                            elif k == 'remarks':
                                nonbillableTS.remarks = v
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
                        # billableTS.approved = True
                        # billableTS.managerFeedback = 'System Approved'
                        billableTS.hold = True
                        billableTS.approvedon = datetime.now().replace(
                            tzinfo=utc)
                    else:
                        billableTS.approved = False
                        billableTS.hold = False
                    for k, v in eachTimesheet.iteritems():
                        if k != 'hold' and k != 'approved':
                            if k in (
                                    'mondayH', 'tuesdayH', 'wednesdayH', 'thursdayH', 'fridayH', 'saturdayH',
                                    'sundayH'):
                                if v is None:
                                    v = float(0.0)

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
                    request, 'Timesheet approved :' + unicode_to_string(approvedSet))
                hold_button = True
            # if len(autoApprovedSet) > 0:
            #     messages.success(
            #         request, 'Timesheet auto-approved by the system :' +
            #                  unicode_to_string(autoApprovedSet))
            #     hold_button = True
            if len(holdSet) > 0:
                messages.info(
                    request, 'Timesheet sent to your manager :' +
                             unicode_to_string(holdSet))
                hold_button = True
            if len(saveSet) > 0:
                messages.info(
                    request, 'Timesheet has been saved:' +
                             unicode_to_string(saveSet))
                hold_button = False
        else:
            # Switch dates back and forth
            dates = switchWeeks(request)
            tsErrorList = timesheets.errors
            tsContent = [k.cleaned_data for k in timesheets]
            for eachErrorData in tsContent:
                for k, v in eachErrorData.items():
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
        data = get_time_sheet(request)
        return renderTimesheet(request, data)


def get_time_sheet(request, is_approve=False):
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
            request, 'Timesheet approved :' + unicode_to_string(approvedSet))
        hold_button = True
    if len(holdSet) > 0:
        messages.info(
            request, 'Timesheet pending manager approval :' +
                     unicode_to_string(holdSet))
        hold_button = True
    if len(sentBackSet) > 0:
        messages.info(
            request, 'Timesheet you have to submit:' + unicode_to_string(sentBackSet))
        # str(list(sentBackSet)))
        hold_button = False

    data = {'weekstartDate': dates['start'],
            'weekendDate': dates['end'],
            'disabled': dates['disabled'],
            'extra': extra,
            'hold_button': hold_button,
            'tsFormList': tsFormList,
            'atFormList': atFormList}
    # is_approve = True
    if not is_approve:
        return data
    else:
        return HttpResponse(
            json.dumps(data),
            content_type="application/json"
        )

def pm_details(request):
    user_details = getTSDataList(request, datetime.strptime(request.GET.get('start_date'), '%d%m%Y').date(),
                      datetime.strptime(request.GET.get('end_date'), '%d%m%Y').date(), request.GET.get('user_id'))
    return HttpResponse(
        json.dumps(user_details),
        content_type="application/json"
    )

def time_sheet_employee(request):
    s = getTSDataList(request, datetime.strptime(request.GET.get('start_date'), '%d%m%Y').date(),
                      datetime.strptime(request.GET.get('end_date'), '%d%m%Y').date(), request.GET.get('user_id'))
    return HttpResponse(
        json.dumps(s),
        content_type="application/json"
    )


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
            request.GET.get('enddate'), '%d%m%Y'
        ).date() + timedelta(days=7)
        if (datetime.now().date() - ansrEndDate).days < 0:
            disabled = 'next'
        else:
            disabled = ''
    elif request.GET.get('startdate'):

        weekstartDate = datetime.strptime(request.GET.get('startdate'), '%d%m%Y').date()
        ansrEndDate = datetime.strptime(request.GET.get('enddate'), '%d%m%Y').date()
        if (datetime.now().date() - ansrEndDate).days < 0:
            disabled = 'next'
        else:
            disabled = ''

    return {'start': weekstartDate, 'end': ansrEndDate, 'disabled': disabled}


def get_activity_hours(user, weekstartDate, ansrEndDate):
    return TimeSheetEntry.objects.filter(
        Q(
            wkstart=weekstartDate,
            wkend=ansrEndDate,
            teamMember=user,
            project__isnull=True
        )
    ).values('id', 'activity', 'mondayH', 'tuesdayH', 'wednesdayH',
             'thursdayH', 'fridayH', 'saturdayH', 'sundayH', 'totalH',
             'managerFeedback', 'approved', 'hold'
             )


def leaveappliedinweek(user, wkstart, wkend):
    weekleave = []
    for single_date in daterange(wkstart, wkend):
        flag = leavecheck(user, single_date)
        if flag == 1:
            weekleave.append(4)
        elif flag == 2:
            weekleave.append(8)
        elif flag == 4:
            weekleave.append(2)
        else:
            weekleave.append(0)
    return weekleave


def time_sheet_for_the_week(week_start_date, week_end_date, request_object, approve_time_sheet=False, dm_projects=None,
                            include_activity=False):

    ts_obj = TimeSheetEntry.objects.filter(wkstart=week_start_date, wkend=week_end_date,
                                           teamMember=request_object.user)

    if approve_time_sheet:

        ts_obj = ts_obj.filter(hold=True)

        if include_activity:
            if dm_projects and dm_projects is not None:
                ts_obj = ts_obj.filter(Q(project__isnull=True) | Q(project__in=dm_projects))
            else:
                ts_obj = ts_obj.filter(Q(project__isnull=True))

        else:
            if dm_projects and dm_projects is not None:
                ts_obj = ts_obj.filter(project__in=dm_projects)

            else:
                ts_obj = []
    return ts_obj

def time_week(week_start_date, week_end_date, request_object):

    ts_obj = TimeSheetEntry.objects.filter(wkstart=week_start_date, wkend=week_end_date,
                                           teamMember=request_object.user)

    return ts_obj


def billable_hours(ts_obj):
    return ts_obj.filter(
        activity__isnull=True,
        task__taskType__in=['B', 'N']
    ).values('totalH', 'project__totalValue', 'project__internal')


def billable_value(billable_hours_obj):
    b_total = 0
    internal_value = 0
    external_value = 0
    for billable in billable_hours_obj:
        if billable['project__internal'] == 1:
            internal_value += billable['totalH']
        else:
            external_value += billable['totalH']
        b_total += billable['totalH']
    return internal_value, external_value, b_total


def non_billable_hours(ts_obj):
    return ts_obj.filter(
        project__isnull=True
    ).values('totalH')


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


class ChangeProjectWizard(SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'ProjectChangeDocument'))
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
            project_detail = ProjectDetail.objects.select_related('project').filter(Q(deliveryManager=self.request.user) | Q(pmDelegate=self.request.user),
                                                                                    project__closed=False).values(
                'project_id')
            project = Project.objects.filter(id__in=project_detail, active=True)
            form.fields['project'].queryset = project

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
                    'startDate',
                )[0]
                currentProject['revisedTotal'] = currentProject['totalValue']
                currentProject['revisedEffort'] = currentProject['plannedEffort']
        return self.initial_dict.get(step, currentProject)

    def done(self, form_list, **kwargs):
        self.request.session['revisedsow'] = self.request.FILES.get('Change Basic Information-Sowdocument', "")
        self.request.session['revisedestimation'] = self.request.FILES.get('Change Basic Information-estimationDocument', "")
        data = UpdateProjectInfo(
            self.request, [
                form.cleaned_data for form in form_list])
        return render(
            self.request,
            'MyANSRSource/changeProjectId.html',
            data)


class ModifyProjectWizard(SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'ProjectChangeDocument'))

    def get_template_names(self):
        return [MTEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super(ModifyProjectWizard, self).get_context_data(
            form=form, **kwargs)
        return context

    def get_form(self, step=None, data=None, files=None):
        form = super(ModifyProjectWizard, self).get_form(step, data, files)
        step = step if step else self.steps.current
        if step == 'Rejected Projects':
            try:
                project_detail = ProjectDetail.objects.select_related('project').filter(Q(deliveryManager=self.request.user) | Q(pmDelegate=self.request.user) | Q(project__bu__new_bu_head=self.request.user),
                                                                                    project__closed=False, project__rejected=True).filter(project__active=False).values('project_id')
            except Exception as e:
                project_detail = []
            project = Project.objects.filter(id__in=project_detail)
            form.queryset = project
        return form

    def get_form_initial(self, step):
        data = self.storage.get_step_data('Rejected Projects')
        if data is not None:
            currentProject = []
            if step == 'Modify Basic Information':

                projectId = data['projectid']
                if projectId is not None:
                    pm = Project.objects.filter(id=projectId).values(
                        'projectManager',
                    )
                    l = []
                    for eachData in pm:
                        l.append(eachData['projectManager'])
                    currentProject = Project.objects.filter(
                        pk=projectId).values(
                        'id',
                        'signed',
                        'endDate',
                        'plannedEffort',
                        'totalValue',
                        'startDate',
                        'salesForceNumber',
                        'plannedEffort',
                        'po',
                        'customer',
                        'bu',
                        'customerContact',
                        'projectType',
                        'book',
                        'totalValue',
                        'name',
                        'currentProject',
                    )[0]
                    additional_detail = ProjectDetail.objects.filter(project_id=projectId).values('projectFinType',
                                                                                                  'Discipline',
                                                                                                  'deliveryManager',
                                                                                                  'outsource_contract_value',
                                                                                                  'pmDelegate')[0]
                    currentProject['projectFinType'] = additional_detail['projectFinType']
                    currentProject['Discipline'] = additional_detail['Discipline']
                    currentProject['DeliveryManager'] = additional_detail['deliveryManager']
                    currentProject['pmDelegate'] = additional_detail['pmDelegate']
                    currentProject['outsource_contract_value'] = additional_detail['outsource_contract_value']
                    currentProject['projectManager'] = l
                    self.request.session['name'] = currentProject['name']

            return self.initial_dict.get(step, currentProject,)

    def done(self, form_list, **kwargs):
        self.request.session['modifiedsow'] = self.request.FILES.get('Modify Basic Information-Sowdocument', "")
        self.request.session['modifiedstimation'] = self.request.FILES.get('Modify Basic Information-Estimationdocument', "")
        data = modifyProjectInfo(
            self.request, [
                form.cleaned_data for form in form_list])
        return render(
            self.request,
            'MyANSRSource/modifyProjectId.html',
            data)

def append_tsstatus_msg(request, tsSet, msg):
    messages.info(request, msg + str(tsSet))

@login_required
def getTSDataList(request, weekstartDate, ansrEndDate, user_id=None):
    # To be approved TS data
    total_list = []
    if not user_id:
        user = request.user
    else:
        user = user_id
    cwActivityData = TimeSheetEntry.objects.filter(
        Q(
            wkstart=weekstartDate,
            wkend=ansrEndDate,
            teamMember=user,
            project__isnull=True
        )
    ).values('id', 'activity', 'activity__name', 'mondayH', 'tuesdayH', 'wednesdayH',
             'thursdayH', 'fridayH', 'saturdayH', 'sundayH', 'totalH',
             'managerFeedback', 'approved', 'hold', 'teamMember__first_name', 'teamMember__last_name',
             'teamMember__employee__employee_assigned_id', 'remarks'
             )

    if user_id:
        if request.session['dm_projects'] and request.session['dm_projects'] is not None:
            cwTimesheetData = TimeSheetEntry.objects.filter(
                Q(
                    wkstart=weekstartDate,
                    wkend=ansrEndDate,
                    teamMember=user, project__in=request.session['dm_projects'],
                    activity__isnull=True
                )
            ).values('id', 'project', 'project__name', 'task__name', 'mondayH',
                     'tuesdayH', 'wednesdayH',
                     'thursdayH', 'fridayH', 'hold',
                     'saturdayH', 'sundayH', 'approved',
                     'totalH', 'managerFeedback', 'project__internal',
                     'teamMember__first_name', 'teamMember__last_name', 'teamMember__employee__employee_assigned_id',
                     'remarks'
                     )
        else:
            cwTimesheetData = []

        if not request.session['include_activity'][int(user_id)]:
            cwActivityData = {}
    else:
        cwTimesheetData = TimeSheetEntry.objects.filter(
            Q(
                wkstart=weekstartDate,
                wkend=ansrEndDate,
                teamMember=user,
                activity__isnull=True
            )
        ).values('id', 'project', 'project__name', 'location', 'chapter', 'task', 'mondayH',
                 'tuesdayH', 'wednesdayH',
                 'thursdayH', 'fridayH', 'hold',
                 'saturdayH', 'sundayH', 'approved',
                 'totalH', 'managerFeedback', 'project__projectType__code', 'project__internal',
                 'teamMember__employee__employee_assigned_id','teamMember__first_name', 'teamMember__last_name',
                 'remarks'
                 )
    # print cwActivityData
    # Changing data TS data
    tsData = {}
    tsDataList = []
    zero = 0
    non_zero = 0
    monday_total = 0.0
    tuesday_total = 0.0
    wednesday_total = 0.0
    thursday_total = 0.0
    friday_total = 0.0
    saturday_total = 0.0
    sunday_total = 0.0
    for eachData in cwTimesheetData:
        for k, v in eachData.iteritems():
            # print k,v
            if user_id:
                if isinstance(v, Decimal):
                    v = str(v)
            if user_id:

                if k == 'teamMember__employee__employee_assigned_id':
                    tsData['employee_id'] = v
                if k == 'project':
                    tsData['project'] = v
                if k == 'project__name':
                    tsData['project_name'] = v
                if k == 'location':
                    tsData['location'] = v
                if k == 'chapter':
                    tsData['chapter'] = v
                if k == 'task':
                    tsData['task'] = v
                if k == 'mondayH':
                    tsData['mondayH'] = v
                    monday_total += float(v)
                if k == 'tuesdayH':
                    tsData['tuesdayH'] = v
                    tuesday_total += float(v)
                if k == 'wednesdayH':
                    tsData['wednesdayH'] = v
                    wednesday_total += float(v)
                if k == 'thursdayH':
                    tsData['thursdayH'] = v
                    thursday_total += float(v)
                if k == 'fridayH':
                    tsData['fridayH'] = v
                    friday_total += float(v)
                if k == 'saturdayH':
                    tsData['saturdayH'] = v
                    saturday_total += float(v)
                if k == 'sundayH':
                    tsData['sundayH'] = v
                    sunday_total += float(v)

            tsData[k] = v
            if k == 'managerFeedback':
                tsData['feedback'] = v
            if k == 'id':
                tsData['tsId'] = v

            if k == 'project__internal':
                tsData['is_internal'] = int(v)

            if k == 'project__projectType__code':
                tsData['projectType'] = v

        tsDataList.append(tsData.copy())
        tsData.clear()
    atData = {}
    atDataList = []

    for eachData in cwActivityData:
        for k, v in eachData.iteritems():
            if user_id:
                v = str(v)
            if k == 'activity':
                atData['activity'] = v
            if k == 'hold':
                atData['hold'] = v
            if 'monday' in k:
                atData['activity_monday'] = v
                monday_total += float(v)
            if 'tuesday' in k:
                atData['activity_tuesday'] = v
                tuesday_total += float(v)
            if 'wednesday' in k:
                atData['activity_wednesday'] = v
                wednesday_total += float(v)
            if 'thursday' in k:
                atData['activity_thursday'] = v
                thursday_total += float(v)
            if 'friday' in k:
                atData['activity_friday'] = v
                friday_total += float(v)
            if 'saturday' in k:
                atData['activity_saturday'] = v
                saturday_total += float(v)
            if 'sunday' in k:
                atData['activity_sunday'] = v
                sunday_total += float(v)
            if 'total' in k:
                atData['activity_total'] = v
            if k == 'managerFeedback':
                atData['managerFeedback'] = v
            if k == 'activity__name':
                atData['activity__name'] = v
            if k == 'id':
                atData['atId'] = v
            atData[k] = v
        atDataList.append(atData.copy())
        atData.clear()
    if user_id:
        total_list .append({'monday_total': str(round(monday_total, 2)), 'tuesday_total': str(round(tuesday_total, 2)),
                            'wednesday_total': str(round(wednesday_total, 2)), 'thursday_total': str(round(thursday_total, 2)),
                            'friday_total': str(round(friday_total, 2)), 'saturday_total': str(round(saturday_total, 2)),
                            'sunday_total': str(round(sunday_total, 2))})
    return {'tsData': tsDataList, 'atData': atDataList, 'total_list': total_list}


def status_member(team_members, ignore_previous_year=False):
    status = {}
    week_collection = []
    if not ignore_previous_year:
        optional_variable = False
    else:
        optional_variable = True
    for s in weeks_list_till_date(optional_variable):
        for_week = str(str(s[0].day) + "-" + s[0].strftime("%b")) + " - " + \
                   str(str(s[1].day) + "-" + s[1].strftime("%b"))
        week_collection.append(for_week)
        wkstart_list = str(s[0]).split('-')[::-1]
        wkstart = "".join([x for x in wkstart_list])
        wkend_list = str(s[1]).split('-')[::-1]
        wkend = "".join([x for x in wkend_list])
        status[for_week] = {}
        status[for_week]['status'] = {}
        status[for_week]['wkstart'] = wkstart
        status[for_week]['wkend'] = wkend
        for members in team_members:
            status[for_week]['status'][members.user.id] = {}
            try:

                result = TimeSheetEntry.objects.filter(teamMember=members.user, wkstart=s[0], wkend=s[1],
                                                       approved=True).exists()
                # print members.user, result
            except:
                result = False
            status[for_week]['status'][members.user.id] = result
    # print "in function " ,  type(week_collection)
    status_dict = {}
    unapproved_count = 0
    for k, v in status.iteritems():
        status_dict[k] = {}
        status_dict[k]['wkstart'] = {}
        status_dict[k]['wkend'] = {}
        if all(value == True for value in v['status'].values()):
            status_dict[k]['status'] = "approved"
        elif all(value == False for value in v['status'].values()):
            unapproved_count += 1
            status_dict[k]['status'] = "not_approved"
        elif True in v['status'].values() and False in v['status'].values():
            unapproved_count += 1
            status_dict[k]['status'] = "partial"
        status_dict[k]['wkstart'] = v['wkstart']
        status_dict[k]['wkend'] = v['wkend']

    # print json.dumps(status_dict)
    return status_dict, week_collection, unapproved_count


def date_range_picker(request, employee=None):
    mondays_list = [x for x in get_mondays_list_till_date()]

    # list of dict with mentioned ts entry columns
    weeks_timesheetEntry_list = TimeSheetEntry.objects.filter(teamMember=request.user, wkstart__in=mondays_list). \
        values('wkstart', 'wkend', 'hold', 'approved').distinct()

    mondays_list = [str(x.strftime("%b") + "-" + str(x.day)) for x in mondays_list]

    weeks_list = [x for x in weeks_list_till_date(False)]
    # print weeks_list

    ts_week_info_dict = {}
    for dict_obj in weeks_timesheetEntry_list:
        for_week = str(str(dict_obj['wkstart'].day) + "-" + dict_obj['wkstart'].strftime("%b")) + " - " + \
                   str(str(dict_obj['wkend'].day) + "-" + dict_obj['wkend'].strftime("%b"))
        dict_obj['for_week'] = for_week
        dict_obj['filled'] = True
        wkstart = str(dict_obj['wkstart']).split('-')[::-1]
        not_submitted = TimeSheetEntry.objects.filter(teamMember=request.user, wkstart=dict_obj['wkstart'],
                                                      hold=False).exists()
        if not_submitted:
            dict_obj['hold'] = False
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
            ts_final_list.append({'for_week': for_week, 'wkstart': "".join([x for x in wkstart]),
                                  'wkend': "".join([x for x in wkend]), 'filled': False})
    # print ts_final_list
    return ts_final_list, mondays_list, ts_week_info_dict


def renderTimesheet(request, data):
    ts_final_list, mondays_list, ts_week_info_dict = date_range_picker(request)
    attendance = {}
    tsObj = time_sheet_for_the_week(data['weekstartDate'], data['weekendDate'], request)
    billableHours = billable_hours(tsObj)
    idleHours = tsObj.filter(
        activity__isnull=True,
        task__taskType='I'
    ).values('totalH')
    othersHours = tsObj.filter(
        project__isnull=True
    ).values('totalH')

    internal_value, external_value, bTotal = billable_value(billableHours)
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
    endDate1 = request.GET.get('enddate', '')
    date = datetime.now().date()
    if request.GET.get("week") == 'prev':
        endDate1 = request.GET.get('enddate', '')
        date = datetime.now().date()
        if endDate1:
            date = datetime(year=int(endDate1[4:8]), month=int(endDate1[2:4]), day=int(endDate1[0:2]))
            date -= timedelta(days=13)
        else:
            date = data['weekstartDate']

    elif request.GET.get("week") == 'next':
        endDate1 = request.GET.get('enddate', '')
        date = datetime.now().date()
        if endDate1:
            date = datetime(year=int(endDate1[4:8]), month=int(endDate1[2:4]), day=int(endDate1[0:2]))
            date += timedelta(days=1)
        else:
            date = data['weekstartDate']

    else:
        date = data['weekstartDate']
    try:
        feedback = TimeSheetEntry.objects.filter(teamMember=request.user, wkstart=data['weekstartDate'],
                                                 wkend=data['weekendDate']).values_list('managerFeedback', flat=True)[0]
    except:
        feedback = ""
    tsform = TimesheetFormset(request.user, date)
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
    leave_hours = pull_members_week(request, data['weekstartDate'], data['weekendDate'])
    leave_hours = float(leave_hours)
    total_sum = leave_hours + float(total)
    finalData = {'weekstartDate': data['weekstartDate'],
                 'weekendDate': data['weekendDate'],
                 'disabled': data['disabled'],
                 'shortDays': ['Mon', 'Tue', 'Wed', 'Thu',
                               'Fri', 'Sat', 'Sun'],
                 'hold_button': data['hold_button'],
                 'billableHours': billableHours,
                 'idleHours': idleHours,
                 'internal_value': internal_value,
                 'external_value': external_value,
                 'bTotal': bTotal,
                 'feedback': feedback,
                 'leave_hours': leave_hours,
                 'idleTotal': idleTotal,
                 'attendance': attendance,
                 'othersTotal': othersTotal,
                 'tsTotal': d,
                 'prevWeekBlock': prevWeekBlock,
                 'total': total_sum,
                 'tsFormset': tsFormset,
                 'atFormset': atFormset,
                 'mondays_list': mondays_list,
                 'ts_week_info_dict': ts_week_info_dict,
                 'ts_final_list': ts_final_list,

                 }
    if 'tsErrorList' in data:
        finalData['tsErrorList'] = data['tsErrorList']
    if 'atErrorList' in data:
        finalData['atErrorList'] = data['atErrorList']

    return render(request, 'MyANSRSource/timesheetEntry.html', finalData)


def pull_members_week(employee, start_date, end_date):
    leave_flag = leaveappliedinweek(employee.user, start_date, end_date)
    # print "leave flag", leave_flag
    leave_hours = 0
    for flag in leave_flag:
        if flag == 4:
            leave_hours += 4
        elif flag == 8:
            leave_hours += 8
        elif flag == 2:
            leave_hours += 2
    # print leave_hours
    return leave_hours


def send_reminder_mail(request):
    email_list = []
    start_date = datetime.strptime(request.GET.get('start_date'), '%d%m%Y').date()
    end_date = datetime.strptime(request.GET.get('end_date'), '%d%m%Y').date()
    manager_team_members, team_members = dem_members(request)
    try:
        # team_dict = {members[0]: members[1] for members in manager_team_members if members[1] not in team_members}
        own_team = {members.user: members.user.email for members in team_members}
        # updated_dict = team_dict.copy()
        # updated_dict.update(own_team)
        for user, email in own_team.iteritems():
            result = TimeSheetEntry.objects.filter(wkstart=start_date, wkend=end_date,
                                                   teamMember=user, hold=True).exists()
            if not result and email not in email_list:
                email_list.append(email)
        TimeSheetWeeklyReminder.delay(request.user, email_list, start_date, end_date)
        json_obj = {'status': True}
    except Exception as e:
        logger.error(
            u'send_reminder_mail function error {0}'.format(
                str(e))
        )
        json_obj = {'status': False}
    return HttpResponse(json.dumps(json_obj), content_type="application/javascript")

def dem_members(request, pm_view=0):
    if pm_view == 1:
        manager = Employee.objects.get(user_id=request.user)
        manager_team_members = Employee.objects.filter((Q(manager_id=manager) |
                                                        Q(employee_assigned_id=manager)),
                                                       user__is_active=True).values_list('user_id', 'user__email')

        return manager_team_members
    else:
        dm_projects = ProjectDetail.objects.filter(Q(deliveryManager=request.user) | Q(pmDelegate=request.user)).values_list('project', flat=True)
        manager = Employee.objects.get(user_id=request.user)
        # to fetch non project activities for their respective team
        manager_team_members = Employee.objects.filter((Q(manager_id=manager) |
                                                        Q(employee_assigned_id=manager)),
                                                       user__is_active=True).values_list('user_id', 'user__email')
        if 'dm_projects' not in request.session:
            if dm_projects:
                request.session['dm_projects'] = dm_projects
            else:
                request.session['dm_projects'] = None
        if dm_projects:
            # allowing DM to approve their ts entry for their own project by removing exclude condition
            team_members = Employee.objects.filter(user__in=ProjectTeamMember.objects.filter(project__in=dm_projects,
                                                                                             member__is_active=True).
                                                   values_list('member', flat=True))  # .exclude(user=request.user)

        else:
            # their own team
            team_members = Employee.objects.filter((Q(manager_id=manager) | Q(employee_assigned_id=manager)),
                                                   user__is_active=True)  # .exclude(user=request.user)

        return manager_team_members, team_members

def pm_view(request):
    if request.method == 'GET':
        context = {}
        ts_final_list, mondays_list, ts_week_info_dict = date_range_picker(request)
        team_members = dem_members(request, pm_view=1)
        team_dict = {members[0]: members[1] for members in team_members}
        # own_team = {members.user_id: members.user.email for members in team_members}
        updated_dict = team_dict.copy()
        # updated_dict.update(own_team)

        user_id_collection = [k[0] for k in team_members]
        if updated_dict:
            dates = switchWeeks(request)
            ts_data_list = {}
            request.session['include_activity'] = {}
            start_date = dates['start']
            end_date = dates['end']
            status, week_collection, unapproved_count = status_member(Employee.objects.filter(
                user_id__in=updated_dict.keys()))
            for user_id, name in updated_dict.iteritems():
                non_billable_total = 0.0
                if user_id not in user_id_collection:
                    include_activity = False
                    request.session['include_activity'][int(user_id)] = False
                else:
                    include_activity = True
                    request.session['include_activity'][int(user_id)] = True

                # exclude dm non project activities from dashboard
                if user_id == request.user.id and request.user.id in updated_dict:
                    request.session['include_activity'][int(request.user.id)] = False

                members = Employee.objects.get(user=user_id)
                ts_obj = time_week(start_date, end_date, members)
                if ts_obj:
                    ts_data_list[members] = {}
                    status_tmp = [s.approved for s in ts_obj]
                    if all(status_tmp):
                        ts_data_list[members]['approved_status'] = True
                    else:
                        ts_data_list[members]['approved_status'] = False

                    if members.user_id not in user_id_collection:
                        non_billable_total = 0
                    else:
                        non_billable_obj = non_billable_hours(ts_obj)
                        for others in non_billable_obj:
                            non_billable_total += float(others['totalH'])
                    ts_data_list[members]['non_billable_total'] = non_billable_total
                    billable_hours_obj = billable_hours(ts_obj)
                    internal_value, external_value, b_total = billable_value(billable_hours_obj)
                    ts_data_list[members]['internal_value'] = internal_value
                    ts_data_list[members]['external_value'] = external_value
                    ts_data_list[members]['b_total'] = b_total
                    ts_data_list[members]['leave_hours'] = pull_members_week(members, start_date, end_date)
                context['ts_data_list'] = ts_data_list
                context['ts_final_list'] = ts_final_list
                context['weekstartDate'] = dates['start']
                context['weekendDate'] = dates['end']
                context['status_dict'] = status
                context['disabled'] = dates['disabled']
            context['week_collection'] = week_collection[::-1]
            ts_data_list_approved_false = {}
            ts_data_list_approved_true = {}

            for k, v in ts_data_list.iteritems():

                if v['approved_status']:
                    ts_data_list_approved_true[k] = v
                else:
                    ts_data_list_approved_false[k] = v
            context['ts_data_list_approved_false'] = ts_data_list_approved_false
            context['ts_data_list_approved_true'] = ts_data_list_approved_true
        else:
            context['exception_message'] = "you don't have any team members"
    return render(request, 'pmview.html', context)

class ApproveTimesheetView(TemplateView):
    template_name = "MyANSRSource/timesheetApprove.html"

    def get_context_data(self, **kwargs):
        context = super(ApproveTimesheetView, self).get_context_data(**kwargs)
        ts_final_list, mondays_list, ts_week_info_dict = date_range_picker(self.request)
        manager_team_members, team_members = dem_members(self.request, pm_view=0)
        team_dict = {members[0]: members[1] for members in manager_team_members if members[1] not in team_members}
        own_team = {members.user_id: members.user.email for members in team_members}
        updated_dict = team_dict.copy()
        updated_dict.update(own_team)

        user_id_collection = [k[0] for k in manager_team_members]
        if updated_dict:
            dates = switchWeeks(self.request)
            ts_data_list = {}
            self.request.session['include_activity'] = {}
            start_date = dates['start']
            end_date = dates['end']
            status, week_collection, unapproved_count = status_member(Employee.objects.filter(
                user_id__in=updated_dict.keys()))
            for user_id, name in updated_dict.iteritems():
                non_billable_total = 0.0
                if user_id not in user_id_collection:
                    include_activity = False
                    self.request.session['include_activity'][int(user_id)] = False
                else:
                    include_activity = True
                    self.request.session['include_activity'][int(user_id)] = True

                # exclude dm non project activities from dashboard
                if user_id == self.request.user.id and self.request.user.id in updated_dict:
                    self.request.session['include_activity'][int(self.request.user.id)] = False

                members = Employee.objects.get(user=user_id)
                ts_obj = time_sheet_for_the_week(start_date, end_date, members, True,
                                                 self.request.session['dm_projects'], include_activity)
                if ts_obj:
                    ts_data_list[members] = {}
                    status_tmp = [s.approved for s in ts_obj]
                    if all(status_tmp):
                        ts_data_list[members]['approved_status'] = True
                    else:
                        ts_data_list[members]['approved_status'] = False

                    if members.user_id not in user_id_collection:
                        non_billable_total = 0
                    else:
                        non_billable_obj = non_billable_hours(ts_obj)
                        for others in non_billable_obj:
                            non_billable_total += float(others['totalH'])
                    ts_data_list[members]['non_billable_total'] = non_billable_total
                    billable_hours_obj = billable_hours(ts_obj)
                    internal_value, external_value, b_total = billable_value(billable_hours_obj)
                    ts_data_list[members]['internal_value'] = internal_value
                    ts_data_list[members]['external_value'] = external_value
                    ts_data_list[members]['b_total'] = b_total
                    ts_data_list[members]['leave_hours'] = pull_members_week(members, start_date, end_date)
                context['ts_data_list'] = ts_data_list
                context['ts_final_list'] = ts_final_list
                context['weekstartDate'] = dates['start']
                context['weekendDate'] = dates['end']
                context['status_dict'] = status
                context['disabled'] = dates['disabled']
            context['week_collection'] = week_collection[::-1]
            ts_data_list_approved_false = {}
            ts_data_list_approved_true = {}

            for k, v in ts_data_list.iteritems():

                if v['approved_status']:
                    ts_data_list_approved_true[k] = v
                else:
                    ts_data_list_approved_false[k] = v
            context['ts_data_list_approved_false'] = ts_data_list_approved_false
            context['ts_data_list_approved_true'] = ts_data_list_approved_true
        else:
            context['exception_message'] = "you don't have any team members"
        return context

    def post(self, request, **kwargs):
        fail = 0
        approve_list = request.POST.getlist('approve[]')
        reject_list = request.POST.getlist('reject[]')
        feedback = {k: v for k, v in self.request.POST.items() if k.startswith('feedback_')}
        start_date = datetime.strptime(
            self.request.POST.get('weekstartDate'), '%d%m%Y'
        ).date()
        end_date = datetime.strptime(
            self.request.POST.get('weekendDate'), '%d%m%Y'
        ).date()
        feedback_dict = {}

        for k, v in feedback.iteritems():
            user_id = k.split('_')
            feedback_dict[user_id[1]] = v
        if approve_list:
            for user_id in approve_list:
                try:
                    if request.session['dm_projects'] and request.session['dm_projects'] is not None:
                        if not request.session["include_activity"][int(user_id)]:
                            TimeSheetEntry.objects.filter(wkstart=start_date, wkend=end_date,
                                                          project__in=request.session['dm_projects'],
                                                          teamMember_id=user_id).update(
                                managerFeedback=feedback_dict[user_id], approved=True)

                        else:
                            TimeSheetEntry.objects.filter(Q(project__in=request.session['dm_projects'])
                                                          |Q(project__isnull=True), wkstart=start_date,
                                                          wkend=end_date, teamMember_id=user_id).update(
                                managerFeedback=feedback_dict[user_id], approved=True)
                    else:
                        # get manager obj
                        emp = Employee.objects.get(user=request.user)
                        if Employee.objects.filter(user_id=user_id, manager=emp.employee_assigned_id).exists():
                            TimeSheetEntry.objects.filter(project__isnull=True, wkstart=start_date,
                                                          wkend=end_date, teamMember_id=user_id).update(
                                managerFeedback=feedback_dict[user_id], approved=True)
                        else:
                            fail += 1
                except Exception as e:
                    fail += 1
                    logger.error(
                        u'Unable to make changes(approve) for time sheet approval  {0}{1}{2} and the error is  {3} '
                        u' '.format(start_date, end_date, user_id, str(e)))
        if reject_list:
            present_id = []
            for user_id in reject_list:
                try:
                    activities = TimeSheetEntry.objects.filter(teamMember_id=user_id, wkstart=start_date, hold=True,
                                                               wkend=end_date, project__isnull=True). \
                        values_list('activity__name', flat=True)
                    a = [str(s) for s in activities]
                    if request.session['dm_projects'] and request.session['dm_projects'] is not None:
                        for proj in request.session['dm_projects']:

                            if TimeSheetEntry.objects.filter(wkstart=start_date, wkend=end_date,
                                                             teamMember_id=user_id, project_id=proj).exists():
                                present_id.append(proj)
                        if present_id:
                            projects = Project.objects.filter(pk__in=present_id)
                            p = [str(s) for s in projects]
                        else:
                            p = []
                        if not request.session["include_activity"][int(user_id)]:
                            TimeSheetEntry.objects.filter(wkstart=start_date, wkend=end_date,
                                                          teamMember_id=user_id, project__in=present_id
                                                          ).update(managerFeedback=feedback_dict[user_id], hold=False)

                        else:
                            TimeSheetEntry.objects.filter(Q(project__in=present_id) |
                                                          Q(project__isnull=True), wkstart=start_date, wkend=end_date,
                                                          teamMember_id=user_id,
                                                          ).update(managerFeedback=feedback_dict[user_id], hold=False)

                            p.extend(a)

                    else:
                        # get manager obj
                        emp = Employee.objects.get(user=request.user)
                        if Employee.objects.filter(user_id=user_id, manager=emp.employee_assigned_id).exists():
                            TimeSheetEntry.objects.filter(wkstart=start_date, wkend=end_date, project__isnull=True,
                                                          teamMember_id=user_id).update(
                                managerFeedback=feedback_dict[user_id],
                                hold=False)
                            p = a
                        else:
                            p = []

                    fail = 0
                    user_obj = User.objects.get(id=user_id)
                    if p:
                        projects = ",".join(p)
                        TimeSheetRejectionNotification.delay(request.user,
                                                             str(user_obj.email), start_date,
                                                             end_date, projects, feedback_dict[user_id])
                    else:
                        fail += 1
                except Exception as e:
                    fail += 1
                    # print str(e)
                    logger.error(
                        u'Unable to make changes(reject) for time sheet approval  {0}{1}{2} and the error is  {3}'
                        u' '.format(start_date, end_date, user_id, str(e)))
        if fail == 0:
            messages.success(self.request, "Records updated Successfully")
        else:
            messages.error(self.request, "Unable  to Process The Records ")
        return HttpResponseRedirect('/myansrsource/timesheet/approve?startdate=' + self.request.POST.get(
            'weekstartDate') + '&enddate=' + self.request.POST.get('weekendDate') + '')


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
    currentTime = datetime.now()
    current_hour = currentTime.hour
    if current_hour < 12:
        greeting = "Good Morning, "+request.user.get_full_name()
    elif 12 <= current_hour < 16:
        greeting = "Good Afternoon, " + request.user.get_full_name()
    else:
        greeting = "Good Evening, " + request.user.get_full_name()

    birthdays_list = Employee.objects.filter(date_of_birthO__day=todays_date.day,
                                             date_of_birthO__month=todays_date.month, user_id__is_active=True)
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
    # btg = BTGReportForm()
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
        'name',
        'milestoneDate')
    nonfinancialM = pm.filter(
        financial=False).values(
        'name',
        'milestoneDate')

    for eachRec in financialM:
        eachRec['milestoneDate'] = eachRec['milestoneDate'].strftime('%Y-%m-%d')
    for eachRec in nonfinancialM:
        eachRec['milestoneDate'] = eachRec['milestoneDate'].strftime('%Y-%m-%d')

    weeks_list = [x for x in weeks_list_till_date()]
    count = 0
    for s, e in weeks_list:
        result = TimeSheetEntry.objects.filter(teamMember=request.user, wkstart=s, wkend=e, hold=True).exists()
        if not result:
            count += 1
    TSProjectsCount = count
    request.session['TSProjectsCount'] = TSProjectsCount

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
        # project__closed=False
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

    currYear = today.year
    currMonth = today.month
    currDay = today.day
    eddte = datetime(int(currYear), int(currMonth), int(currDay))
    attendenceDetail = employee.models.Attendance.objects.filter(
        attdate__lte=eddte,
        employee_id__user_id=request.user.id).values('swipe_in', 'swipe_out', 'attdate').filter(
        Q(swipe_in__isnull=False) & Q(swipe_out__isnull=False) & Q(
            attdate__isnull=False))  # .exclude(swipe_in="", swipe_out="", attdate="")
    swipe_display = []

    for val in attendenceDetail:
        temp = {}
        temp['date'] = val['attdate'].strftime('%Y-%m-%d')
        temp['swipe_in'] = val['swipe_in']
        temp['swipe_out'] = val['swipe_out']
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
        manager=request.user.employee, user__is_active=True)
    isManager = 0
    employee_color = Employee.objects.get(user_id=request.user.id)
    if employee_color.color:
        employee_color = employee_color.color
    else:
        employee_color = ''
    request.session['color'] = employee_color
    if myReportee:
        isManager = 1
    team_members = Employee.objects.filter((Q(manager_id=request.user.employee) |
                                            Q(employee_assigned_id=request.user.employee)), user__is_active=True)
    request.session['unapprovedts'] = status_member(myReportee, True)[2]
    data = {
        'greeting' : greeting,
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
        'unapprovedts': request.session['unapprovedts'],
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
            project_detail = ProjectDetail.objects.select_related('project').filter(Q(deliveryManager=self.request.user) | Q(pmDelegate=self.request.user),
                                                                                    project__closed=False).values(
                'project_id')
            project = Project.objects.filter(id__in=project_detail)
            form.fields['project'].queryset = project
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
            delivery_delegate_mgr = ProjectDetail.objects.filter(project=myProject.id).values('deliveryManager','pmDelegate')[0]
            projectMS = {'projectManager': l, 'DeliveryManager': delivery_delegate_mgr['deliveryManager'], 'pmDelegate': delivery_delegate_mgr['pmDelegate']}
            return self.initial_dict.get(step, projectMS)

    def done(self, form_list, **kwargs):
        updatedData = [form.cleaned_data for form in form_list][1]
        myProject = self.get_cleaned_data_for_step('My Projects')['project']
        myProject = Project.objects.get(id=myProject.id)
        allData = ProjectManager.objects.filter(
            project=myProject).values('id', 'user')
        updateDataId = [eachData.id for eachData in updatedData['projectManager']]
        try:
            ProjectDetail.objects.filter(project=myProject.id).update(deliveryManager=updatedData['DeliveryManager'],
                                                                      pmDelegate=updatedData['pmDelegate'])
        except Exception as error:
            logger.error(error)
        for eachData in allData:
            if eachData['user'] not in updateDataId:
                ProjectManager.objects.get(pk=eachData['id']).delete()
        for eachData in updatedData['projectManager']:
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


class TrackMilestoneWizardDelivery(SessionWizardView):
    def get_template_names(self):
        return [TMTEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super(TrackMilestoneWizardDelivery, self).get_context_data(
            form=form, **kwargs)
        if self.steps.current == 'Manage Milestones':
            selectedProjectId = self.storage.get_step_data(
                'My Projects'
            )['My Projects-project']
            projectObj = Project.objects.get(pk=selectedProjectId)
            totalValue = projectObj.totalValue
            projectType = projectObj.internal
            projectname = projectObj.name
            context.update({'totalValue': totalValue, 'type': projectType, 'name': projectname})
        return context

    def get_form(self, step=None, data=None, files=None):
        form = super(TrackMilestoneWizardDelivery, self).get_form(step, data, files)
        step = step if step else self.steps.current
        if step == 'My Projects':
            project_detail = ProjectDetail.objects.select_related('project').filter(Q(deliveryManager=self.request.user) | Q(pmDelegate=self.request.user),
                                                                                    project__closed=False).values(
                'project_id')
            project = Project.objects.filter(id__in=project_detail, active=True)
            form.fields['project'].queryset = project
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
                            if eachForm['closed'].value():
                                continue
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
                project__id=selectedProjectId, financial = False,
            ).values(
                'id',
                'name',
                'milestoneDate',
                'description',
                'unit',
                'rate_per_unit',
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
                        SaveDelivery(self, pm, eachData, projectObj)
                else:
                    pm = ProjectMilestone()
                    if eachData['DELETE']:
                        pass
                    else:
                        SaveDelivery(self, pm, eachData, projectObj)
        else:
            logging.error("Request: " + self.request)
        return HttpResponseRedirect('/myansrsource/dashboard')


def SaveDelivery(self, pm, eachData, projectObj):
    if pm.closed:
        pass
    else:
        pm.rate_per_unit = eachData['rate_per_unit']
        pm.unit = eachData['unit']
        pm.project = projectObj
        pm.name = eachData['name']
        pm.description = eachData['description']
        pm.milestoneDate = eachData['milestoneDate']
        pm.amount = eachData['amount']
        pm.closed = eachData['closed']
        pm.financial = False
        pm.save(self.request)


TrackMilestoneDelivery = TrackMilestoneWizardDelivery.as_view(TMFORMSDELIVERY)

@login_required
@permission_required('MyANSRSource.manage_project')
def WrappedTrackMilestoneViewDelivery(request):
    return TrackMilestoneDelivery(request)

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
            projectname = projectObj.name
            context.update({'totalValue': totalValue, 'type': projectType, 'name': projectname})
        return context

    def get_form(self, step=None, data=None, files=None):
        form = super(TrackMilestoneWizard, self).get_form(step, data, files)
        step = step if step else self.steps.current
        if step == 'My Projects':
            project_detail = ProjectDetail.objects.select_related('project').filter(Q(deliveryManager=self.request.user) | Q(pmDelegate=self.request.user),
                                                                                    project__closed=False).values(
                'project_id')
            project = Project.objects.filter(id__in=project_detail, active=True)
            form.fields['project'].queryset = project
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
                            if eachForm['closed'].value():
                                continue
                            milestone_type = Milestone.objects.get(id=eachForm['name'].value()).\
                                milestone_type.\
                                milestone_type
                            if eachForm.cleaned_data['amount'] == 0:
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
                project__id=selectedProjectId, financial = True,
            ).values(
                'id',
                'name',
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
        pm.name = eachData['name']
        pm.description = eachData['description']
        pm.milestoneDate = eachData['milestoneDate']
        pm.amount = eachData['amount']
        pm.closed = eachData['closed']
        pm.financial = True
        pm.save(self.request)


TrackMilestone = TrackMilestoneWizard.as_view(TMFORMS)


@login_required
@permission_required('MyANSRSource.manage_milestones')
def WrappedTrackMilestoneView(request):
    return TrackMilestone(request)


def UpdateProjectInfo(request, newInfo):
    """
        newInfo[0] ==> Selected Project Object
        newInfo[1] ==> 'reason' , 'endDate', 'revisedEffort', 'revisedTotal',
                       'closed', 'signed'
    """
    try:
        pru = newInfo[0]['project']
        pci = ProjectChangeInfo()
        pci.project = pru
        if newInfo[1]['remark']:
            pci.reason = newInfo[1]['remark']
        else:
            pci.reason = newInfo[1]['reason']
        pci.endDate = newInfo[1]['endDate']
        pci.revisedEffort = newInfo[1]['revisedEffort']
        pci.revisedTotal = newInfo[1]['revisedTotal']
        pci.closed = newInfo[1]['closed']
        pci.startDate = newInfo[1]['startDate']
        pci.estimationDocument = request.session['revisedestimation']
        pci.sowdocument = request.session['revisedsow']
        pci.bu = pru.bu
        pci.approved = 0
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


def modifyProjectInfo(request, newInfo):
    try:
        ProjectName = Project.objects.filter(id=newInfo[1]['id']).values('name')[0]
        Project.objects.filter(id=newInfo[1]['id']).update(plannedEffort=newInfo[1]['plannedEffort'],
                                                           totalValue=newInfo[1]['totalValue'],
                                                           endDate=newInfo[1]['endDate'],
                                                           startDate=newInfo[1]['startDate'],
                                                           bu=newInfo[1]['bu'],
                                                           customerContact=newInfo[1]['customerContact'],
                                                           salesForceNumber=newInfo[1]['salesForceNumber'],
                                                           book=newInfo[1]['book'],
                                                           projectType=newInfo[1]['projectType'],
                                                           customer=newInfo[1]['customer'],
                                                           currentProject=newInfo[1]['currentProject'],
                                                           rejected=False,)
        ProjectDetail.objects.filter(project_id=newInfo[1]['id']).update(Discipline=newInfo[1]['Discipline'],
                                                                         projectFinType=newInfo[1]['projectFinType'],
                                                                         deliveryManager=newInfo[1]['DeliveryManager'],
                                                                         pmDelegate=newInfo[1]['pmDelegate'],
                                                                         Estimationdocument=request.session['modifiedstimation'],
                                                                         Sowdocument=request.session['modifiedsow'],
                                                                         )
        myProject = Project.objects.get(id=newInfo[1]['id'])
        allData = ProjectManager.objects.filter(
            project=myProject).values('id', 'user')
        updateDataId = [eachData.id for eachData in newInfo[1]['projectManager']]
        for eachData in allData:
            if eachData['user'] not in updateDataId:
                ProjectManager.objects.get(pk=eachData['id']).delete()
        for eachData in newInfo[1]['projectManager']:
            pm = ProjectManager()
            oldData = ProjectManager.objects.filter(
                project=myProject, user=eachData).values('id')
            if len(oldData):
                pass
            else:
                pm.project = myProject
                pm.user = eachData
                pm.save()

        return {'name': ProjectName['name']}
    except (ProjectTeamMember.DoesNotExist,
            ProjectMilestone.DoesNotExist) as e:
        messages.error(request, 'Could not save change request information')
        logger.error('Exception in ModifyProjectInfo :' + str(e))
        return {'name': None}

changeProject = ChangeProjectWizard.as_view(CFORMS)
modifyProject =ModifyProjectWizard.as_view(MFORMS)


@login_required
@permission_required('MyANSRSource.manage_project')
def WrappedChangeProjectView(request):
    return changeProject(request)

def WrappedModifyProjectView(request):
    return modifyProject(request)


class CreateProjectWizard(SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'ProjectDocument'))

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_form(self, step=None, data=None, files=None):
        form = super(CreateProjectWizard, self).get_form(step, data, files)
        step = step if step else self.steps.current
        if step == 'Define Project' and form.is_valid():
            self.request.session['signed'] = form.cleaned_data['signed']
            self.request.session['PStartDate'] = form.cleaned_data['startDate'].strftime('%Y-%m-%d')
            self.request.session['PEndDate'] = form.cleaned_data['endDate'].strftime('%Y-%m-%d')
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
        if step == 'Uploads':
            if form.is_valid():
                self.request.session['sow'] = self.request.FILES.get('Uploads-Sowdocument', "")
                self.request.session['estimation'] = self.request.FILES.get('Uploads-Estimationdocument', "")


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
                                        if eachForm.cleaned_data['name'].milestone_type.milestone_type in\
                                                ['Financial',]:
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
        upload = [form.cleaned_data for form in form_list][2]
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
        # if flagData['practicename']:
        #     head_id = Practice.objects.select_related('head').get(name=flagData['practicename']).head_id
        #     head = User.objects.get(id=head_id);
        #     head_name = head.first_name + " " + head.last_name
        #     practicehead_name = head_name
        # else:
        #     practicehead_name = 'None'
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
            'upload': upload,
            'practicehead_name':'None',
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
                    active=True).values('id', 'member','project_id__name',
                                        'startDate', 'endDate',
                                        'role',
                                        'plannedEffort', 'plannedcount', 'product', 'actualcount'
                                        )
                try:
                    self.request.session['Pname'] = currentProject[0]['project_id__name']
                except Exception as e:
                    logger.error(e)


            else:
                logger.error(u"Project Id : {0}, Request: {1},".format(
                    projectId, self.request))
        return self.initial_dict.get(step, currentProject)

    def get_context_data(self, form, **kwargs):
        context = super(ManageTeamWizard, self).get_context_data(
            form=form, **kwargs)
        if self.steps.current == 'My Projects':
            project_detail = ProjectDetail.objects.select_related('project').filter(Q(deliveryManager=self.request.user) | Q(pmDelegate=self.request.user),
                                                                                    project__closed=False).values(
                'project_id')
            project = Project.objects.filter(id__in=project_detail, active=True)
            form.fields['project'].queryset = project
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
                        eachData['endDate'] = eachData['startDate']+ timedelta(days=7)
                        ptm = ProjectTeamMember.objects.get(pk=eachData['id'])
                        if (eachData['startDate'] == ptm.startDate) and \
                                (eachData['plannedEffort'] == ptm.plannedEffort) and \
                                (eachData['member'] == ptm.member) and \
                                (eachData['product']== ptm.product) and \
                                (eachData['endDate'] == ptm.endDate) and \
                                (eachData['plannedcount'] == ptm.plannedcount) and \
                                (eachData['role'] == ptm.role):
                            pass
                        else:
                            ptm.project = project
                            del (eachData['id'])
                            for k, v in eachData.iteritems():
                                setattr(ptm, k, v)
                            ptm.save()
                            NotifyMember(ptm.id, False)
                else:
                    ptm = ProjectTeamMember()
                    ptm.project = project
                    del (eachData['id'])
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
    for i in range(0, 1):
        if request.method == 'POST':
            try:
                #: code to check not more than 3 PM per project
                pm = []
                for eachId in eval(request.POST.get('pm')):
                    pm.append(eachId)
                pm_count = len(pm)
                if pm_count > 3:
                    messages.error(request, "OOPS can't select more than 3 ProjectManger")
                    return render(
                        request,
                        'MyANSRSource/projectCreationFailure.html',
                        {})
                pr = Project()
                pr.name = request.POST.get('name')
                pType = projectType.objects.get(
                    id=int(request.POST.get('projectType'))
                )
                pr.projectType = pType
                startDate = request.session['PStartDate']
                endDate = request.session['PEndDate']
                pr.startDate = startDate
                pr.endDate = endDate
                pr.po = request.POST.get('po')
                pr.totalValue = float(request.POST.get('totalValue'))
                pr.plannedEffort = int(request.POST.get('plannedEffort'))
                pr.salesForceNumber = int(request.POST.get('salesForceNumber'))
                pr.currentProject = True if request.POST.get('currentProject') == 'True' else False
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
                try:
                    projectIdPrefix = u"{0}-{1}-{2}".format(
                        pr.customer.customerCode,
                        datetime.now().year,
                        str(pr.customer.seqNumber).zfill(3)
                    )
                    pr.projectId = projectIdPrefix
                    pr.save()
                except Exception as er:
                    print er
                pr.customer.seqNumber = pr.customer.seqNumber + 1
                pr.customer.save()

                pci = ProjectChangeInfo()
                pci.project = pr
                pci.crId = u"BL-{0}".format(pr.id)
                pci.reason = 'Base Line data'
                pci.endDate = endDate
                pci.revisedEffort = int(request.POST.get('plannedEffort'))
                pci.revisedTotal = float(request.POST.get('totalValue'))
                pci.salesForceNumber = int(request.POST.get('salesForceNumber'))
                pci.save()

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

                try:
                    pd = ProjectDetail()
                    pd.project_id = pr.id
                    pd.projecttemplate = ProjectSopTemplate.objects.get(name=request.POST.get('projecttemplate'))
                    pd.pmDelegate = User.objects.get(username=request.POST.get('pmDelegate')) if request.POST.get('pmDelegate') != 'None' else None
                    pd.projectFinType = request.POST.get('projectFinType')
                    portfoliomgr = request.POST.get('PortfolioManager')
                    portfolio_mgr_id = User.objects.get(username=portfoliomgr).id
                    pd.portfolio_manager_id = portfolio_mgr_id
                    del_mgr = request.POST.get('DeliveryManager')
                    del_mgr_id = User.objects.get(username=del_mgr).id
                    pd.deliveryManager_id = del_mgr_id
                    pd.Project_funding = request.POST.get('Project_funding') if request.POST.get('Project_funding') != 'None' else None
                    pd.Sowdocument = request.session['sow']
                    pd.Estimationdocument = request.session['estimation']
                    sop = request.POST.get('sopname')
                    sop_id = qualitysop.objects.get(name=sop).id if sop != 'None' else None
                    pd.SOP_id = sop_id
                    scope = request.POST.get('ProjectScope')
                    scope_id = ProjectScope.objects.get(scope=scope).id if scope != 'None' else None
                    pd.Scope_id = scope_id
                    asset = request.POST.get('projectasset')
                    asset_id = ProjectAsset.objects.get(Asset=asset).id if asset != 'None' else None
                    try:

                        template, created = TemplateMaster.objects.get_or_create(name=request.POST.get('projecttemplate'),
                                                                        defaults=
                                                                        {'actual_name': request.POST.get('projecttemplate'),
                                                                        'created_by': request.user})

                        qms_process_model, created = QMSProcessModel.objects.get_or_create(name=sop,
                                                                                  defaults={
                                                                        'created_by': request.user})

                        obj,created = ProjectTemplateProcessModel.objects.update_or_create(project_id=pd.project_id,
                                                                             defaults={
                                                                                 'template': template,

                                                                                 'qms_process_model': qms_process_model,
                                                                                 'created_by': request.user}, )
                    except Exception as e:
                        print str(e)
                    try:
                        pd.Asset_id = asset_id
                    except Exception as e:
                        print e
                    pd.save()

                except ValueError as e:
                    pr.delete()
                    pm.delete()
                    pci.delete()
                    pr.customer.delete()
                    logger.exception(e)
                    return render(
                        request,
                        'MyANSRSource/projectCreationFailure.html',
                        {})


            except ValueError as e:
                logger.exception(e)
                return render(
                    request,
                    'MyANSRSource/projectCreationFailure.html',
                    {})

            data = {'projectCode': projectIdPrefix, 'projectId': pr.id,
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


def project_summary(project_id, show_header=True):
    projectObj = Project.objects.filter(id=project_id)
    basicInfo = projectObj.values(
        'projectType__description', 'bu__name', 'customer__name',
        'name', 'book__name', 'signed', 'internal', 'currentProject',
        'projectId', 'customerContact'
    )[0]
    projdetailobj = ProjectDetail.objects.filter(project_id=project_id)
    if projdetailobj:
        projdetailvalue = projdetailobj.values('projectFinType', 'deliveryManager__username', 'pmDelegate__username')[0]
        basicInfo['projectFinType'] = projdetailvalue['projectFinType']
        basicInfo['deliveryManager'] = projdetailvalue['deliveryManager__username']
        basicInfo['pmDelegate'] = projdetailvalue['pmDelegate__username']
    else:
        basicInfo['projectFinType'] = None
        basicInfo['deliveryManager'] = None
        basicInfo['pmDelegate'] = None
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
        'plannedEffort',
    )
    if basicInfo['internal']:
        cleanedMilestoneDataFinancial = []
        cleanedMilestoneDataDelivery = []
    else:
        try:
            cleanedMilestoneDataFinancial = ProjectMilestone.objects.filter(
                project=projectObj, financial = True).values('milestoneDate', 'description',
                                           'amount', 'name', 'financial', 'closed')
            for element in cleanedMilestoneDataFinancial:
                name_id = element['name']
                name = Milestone.objects.filter(id=name_id)
                if name.exists():
                    element['name'] = name[0]
                else:
                    element['name'] = ''
        except ProjectMilestone.DoesNotExist:
            cleanedMilestoneDataFinancial = []

        try:
            cleanedMilestoneDataDelivery = ProjectMilestone.objects.filter(
                project=projectObj, financial=False).values('milestoneDate', 'description',
                                                           'amount', 'name', 'financial', 'closed')
            for element in cleanedMilestoneDataDelivery:
                name_id = element['name']
                name = Milestone.objects.filter(id = name_id)
                if name.exists():
                    element['name'] = name[0]
                else:
                    element['name'] = ''
        except ProjectMilestone.DoesNotExist:
            cleanedMilestoneDataDelivery = []


    changeTracker = ProjectChangeInfo.objects.filter(
        project=projectObj).values(
        'reason', 'endDate', 'revisedEffort', 'revisedTotal',
        'closed', 'closedOn', 'signed',
        'updatedOn','approved'
    ).order_by('updatedOn')
    data = {
        'basicInfo': basicInfo,
        'flagData': flagData,
        'teamMember': cleanedTeamData,
        'milestone': cleanedMilestoneDataFinancial,
        'milestoneDelivery': cleanedMilestoneDataDelivery,
        'changes': changeTracker,
    }
    if len(changeTracker):
        closedOn = [
            eachRec
            ['closedOn']
            for eachRec in changeTracker if eachRec['closedOn'] is not None]
        if len(closedOn):
            data['closedOn'] = closedOn[0].strftime("%B %d, %Y, %r")
    data['show_header']= show_header
    return data


@login_required
@permission_required('MyANSRSource.create_project')
def ViewProject(request):
    if request.method == 'POST':
        projectId = int(request.POST.get('project'))
        data = project_summary(projectId)
        return render(request, 'MyANSRSource/viewProjectSummary.html', data)

    data2 = ProjectDetail.objects.select_related('project').filter(Q(deliveryManager=request.user)
                                                                   | Q(pmDelegate=request.user) |
                                                                   Q(Discipline__lead=request.user.id))
    allproj =[]
    bu_list = CompanyMaster.models.BusinessUnit.objects.filter(new_bu_head=request.user)
    for val in data2:
        allproj.append(val.project_id)
    project_status = request.GET.get('approve')
    if project_status == 'False':
        data = Project.objects.filter(closed=True,active=True).filter(Q(projectManager=request.user) | Q(id__in=allproj)
                                      | Q(customer__Crelation=request.user.id) | Q(customer__Cdelivery=request.user.id)
                                                                      | Q(bu__in=bu_list)).values(
            'name', 'id', 'closed', 'projectId'
        ).distinct()
    elif project_status == 'True':
        data = Project.objects.filter(closed=False, active=True).filter(Q(projectManager=request.user) | Q(id__in=allproj)
                                                           | Q(customer__Crelation=request.user.id) | Q(customer__Cdelivery=request.user.id)
                                                                        |Q(bu__in=bu_list)).values(
            'name', 'id', 'closed', 'projectId'
        ).distinct()
    else:
        data = Project.objects.filter(closed=False, active=True).filter(Q(projectManager=request.user) | Q(id__in=allproj)
                                                          | Q(customer__Crelation=request.user.id) | Q(customer__Cdelivery=request.user.id)
                                                                       |Q(bu__in=bu_list) ).values(
            'name', 'id', 'closed', 'projectId'
        ).distinct()

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
        ).values('code', 'name', 'id', 'taskType', 'norm').order_by('name')
        for eachRec in tasks:
            eachRec['norm'] = float(eachRec['norm'])
        a1 = request.GET.get('endDate')
        date = datetime(year=int(a1[4:8]), month=int(a1[2:4]), day=int(a1[0:2])).date()
        pEndDate = Project.objects.get(pk=projectid).endDate
        diff = date - pEndDate
        diff = diff.days
        if diff < 0:
            diff = 0
        data = {'data': list(tasks), 'flag': diff}
    except Task.DoesNotExist:
        diff = 0
        data = {'data': list(), 'flag': diff}
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
        strtDate1 = request.GET.get('strtDate')
        date1 = datetime(year=int(strtDate1[4:8]), month=int(strtDate1[2:4]), day=int(strtDate1[0:2])).date()
        typeData = ProjectTeamMember.objects.values(
            'project__id',
            'project__name',
            'project__projectType__code',
            'project__projectType__description'
        ).filter(project__endDate__gte=date1
                 # project__closed=False
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


def is_internal(request):
    try:
        obj = Project.objects.get(pk=request.GET.get('project_id'))
        internal = obj.internal
    except:
        internal = 0
    return HttpResponse(json.dumps({'is_internal': int(internal)}), content_type="application/json")


class NewCreatedProjectApproval(View):
    template_name = "newCreatedProjectApproval.html"

    def get_queryset(self, request):
        business_unit_list = CompanyMaster.models.BusinessUnit.objects.filter(new_bu_head=request.user)
        queryset = Project.objects.filter(bu__in=business_unit_list, active=False, closed=False, rejected=False)
        return queryset

    def get(self, request):
        queryset = self.get_queryset(request)
        return render(request, self.template_name, {'queryset':queryset})

    def post(self, request):
        try:
            feedback_ist = []
            approve = request.POST.getlist('approve[]')
            reject = request.POST.getlist('reject[]')
            feedback = request.POST.getlist('feedback[]')
            for val in feedback:
                feedback_ist.append(val.split('_'))
                Project.objects.filter(id=feedback_ist[0][1]).update(remark=feedback_ist[0][0])
                feedback_ist = []
            approve = approve if approve else []
            reject = reject if reject else []
            Project.objects.filter(id__in=approve).update(active=True)
            Project.objects.filter(id__in=reject).update(rejected=True)
            for val in reject:
                rejection_date = date.today()
                emailvalues = ProjectDetail.objects.filter(project_id=val).values('deliveryManager__email', 'deliveryManager__username', 'project__remark', 'project__name')[0]
                ProjectRejection.delay(emailvalues['deliveryManager__email'], emailvalues['project__remark'], emailvalues['deliveryManager__username'],  emailvalues['project__name'], rejection_date)
            return HttpResponse()
        except Exception as E:
            return HttpResponse(E)


def project_detail(request):
    project_id = request.GET.get('id')
    try:
        project_details = ProjectDetail.objects.select_related('project').get(project_id=project_id)
        return render(request, 'project_detail.html', {'project_detail': project_details})
    except Exception as e:
        return render(request, 'project_detail.html', {'project_detail': 'Nothing'})



'''project Change Bu approval screen'''


class ProjectChangeApproval(View):
    template_name = "projectchangeapproval.html"

    def get_queryset(self, request):
        business_unit_list = CompanyMaster.models.BusinessUnit.objects.filter(new_bu_head=request.user)
        queryset = ProjectChangeInfo.objects.filter(bu__in=business_unit_list, approved=0)
        return queryset

    def get(self, request):
        queryset = self.get_queryset(request)
        return render(request, self.template_name, {'queryset': queryset})

    def post(self, request):
        try:
            approve = request.POST.getlist('approve[]')
            reject = request.POST.getlist('reject[]')
            approve = approve if approve else []
            reject = reject if reject else []
            try:
                ProjectChangeInfo.objects.filter(crId__in=approve).update(approved=1)
                ProjectChangeInfo.objects.filter(crId__in=reject).update(approved=2)
                update_project_table = []
                emailnotifier = []
                for val in reject:
                    rejection_date = date.today()
                    update_project_table = ProjectChangeInfo.objects.filter(crId=val).values('project', 'reason', 'project__name')[0]
                    emailvalues = ProjectDetail.objects.filter(project_id=update_project_table['project']).values('deliveryManager__email', 'pmDelegate__email', 'project__projectManager__email')[0]
                    emailnotifier.append(emailvalues['project__projectManager__email'].encode("utf-8"))
                    emailnotifier.append(emailvalues['deliveryManager__email'].encode("utf-8"))
                    emailnotifier = list(set(emailnotifier))
                    ProjectChangeRejection.delay(emailnotifier, val, update_project_table['reason'], update_project_table['project__name'], rejection_date)
                for val in approve:
                    update_project_table = ProjectChangeInfo.objects.filter(crId=val).values('startDate',
                                                                                             'endDate',
                                                                                             'revisedEffort',
                                                                                             'revisedTotal',
                                                                                             'project', 'signed',
                                                                                             'closed',
                                                                                             )[0]
                    try:
                        Project.objects.filter(id=update_project_table['project']).update(plannedEffort=update_project_table['revisedEffort'],
                                                                                          totalValue=update_project_table['revisedTotal'],
                                                                                          closed=update_project_table['closed'],
                                                                                          signed=update_project_table['signed'],
                                                                                          endDate=update_project_table['endDate'],
                                                                                          startDate=update_project_table['startDate'],
                                                                                          )

                    except Exception as error:
                        return HttpResponse(error)

            except Exception as error:
                return HttpResponse(error)
            return HttpResponse()
        except Exception as E:
            return HttpResponse(E)


def project_change_detail(request):
    cr_id = request.GET.get('id')
    project_change_detail = ProjectChangeInfo.objects.select_related('project').get(crId=cr_id)
    project_change_detail = ProjectChangeInfo.objects.get(crId=cr_id)
    return render(request,'project_change_detail.html', {'project_change_detail': project_change_detail})

month = [(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'),
                 (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')]


class ActiveEmployees(TemplateView):
    template_name = "MyANSRSource/active_employees.html"

    def get_context_data(self, **kwargs):
        context = super(ActiveEmployees, self).get_context_data(**kwargs)
        if self.request.user.groups.filter(name='myansrsourcebuhead').exists():
            context['employees_list'] = Employee.objects.filter(
                user__is_active=True).values(
                                                       'business_unit__name', 'employee_assigned_id',
                                                       'user__first_name', 'user__last_name',
                                                       'manager__user__first_name',
                                                       'manager__user__last_name', 'designation__name',
                                                       'location__name')
            context['month_list'] = month

            return context
        else:
            raise PermissionDenied

    def post(self, request, *args, **kwargs):
        now = datetime.now()
        dict_month = dict(month)
        if request.POST.get('month') != "":
            file_name = str(dict_month[int(request.POST.get('month'))]) + '_active_employees.xlsx'
        else:
            file_name = now.strftime('%B') + '_active_employees.xlsx'

        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet()
        header = ['Employee Id', 'Name', 'Manager', 'Designation', 'Practice', 'Business Unit',  'Location']
        header_length = len(header)
        header_column = list(string.ascii_uppercase)[:header_length]
        header_column = [s+"1" for s in header_column]
        header = zip(header_column, header)

        if request.POST.get('month') != "":
            result = EmployeeArchive.objects.filter(user__is_active=True, archive_date__month=int(request.POST.get('month')),
                                                    archive_date__year=now.year).values_list(
                 'employee_assigned_id', 'user__first_name', 'user__last_name', 'manager__user__first_name',
                 'manager__user__last_name',  'designation__name', 'practice__name', 'business_unit__name',
                 'location__name')
        else:
            result = EmployeeArchive.objects.filter(user__is_active=True,
                                                    archive_date__year=now.year).values_list(
                'employee_assigned_id',
                'user__first_name', 'user__last_name', 'manager__user__first_name',
                'manager__user__last_name', 'designation__name', 'practice__name', 'business_unit__name',
                'location__name')

        for k, v in header:
            worksheet.write(k, v)
        row = 1
        for s in result:
            worksheet.write(row, 0, s[0])
            worksheet.write(row, 1, s[1]+" "+s[2])
            worksheet.write(row, 2, s[3]+" "+s[4])
            worksheet.write(row, 3, s[5])
            worksheet.write(row, 4, s[6])
            worksheet.write(row, 5, s[7])
            worksheet.write(row, 6, s[8])

            row += 1

        workbook.close()

        return generateDownload(self.request, file_name)


@login_required()
def month_wise_active_employees(request):
    if request.user.groups.filter(name='myansrsourcebuhead').exists():
        try:
            now = datetime.now()
            result = EmployeeArchive.objects.filter(user__is_active=True, archive_date__month=request.GET.get('month'),
                                                    archive_date__year=now.year).values(
                                                       'business_unit__name', 'employee_assigned_id',
                                                       'user__first_name', 'user__last_name',
                                                       'manager__user__first_name',
                                                       'manager__user__last_name', 'designation__name',
                                                       'location__name')

            result = json.dumps(list(result), cls=DjangoJSONEncoder)

        except Exception as e:
            logger.error(str(e))
    # print  result
    else:
        raise PermissionDenied

    return HttpResponse(result, content_type="application/json")


class ActiveProjects(TemplateView):
    template_name = "MyANSRSource/active_projects.html"

    def get_context_data(self, **kwargs):
        context = super(ActiveProjects, self).get_context_data(**kwargs)
        if self.request.user.groups.filter(name='myansrsourcebuhead').exists():
            context['projects_list'] = ProjectDetail.objects.filter(
                project__closed=False).values('Discipline__name', 'project__projectId', 'project__name', 'project__id',
                                              'project__customer__name',  'project__bu__name','project__endDate')
            return context
        else:
            raise PermissionDenied

    def post(self, request, *args, **kwargs):
        workbook = xlsxwriter.Workbook('active_projects.xlsx')
        worksheet = workbook.add_worksheet()
        header = ['Project Id', 'Project', 'Discipline', 'Customer', 'Business Unit', 'End Date']
        header_length = len(header)
        header_column = list(string.ascii_uppercase)[:header_length]
        header_column = [s+"1" for s in header_column]
        header = zip(header_column, header)
        date_format = workbook.add_format({'num_format': 'yyyy/mm/dd'})
        project_details = ProjectDetail.objects.filter(
                project__closed=False).values_list('project__projectId',  'project__name',  'Discipline__name',
                                                   'project__customer__name',
                                                   'project__bu__name', 'project__endDate')
        for k, v in header:
            worksheet.write(k, v)
        row = 1
        for s in project_details:
            worksheet.write(row, 0, s[0])
            worksheet.write(row, 1, s[1])
            worksheet.write(row, 2, s[2])
            worksheet.write(row, 3, s[3])
            worksheet.write(row, 4, s[4])
            worksheet.write(row, 5, s[5], date_format)
            row += 1

        workbook.close()

        return generateDownload(self.request, 'active_projects.xlsx')


@login_required()
def get_project_summary(request, project_id):
    if request.user.groups.filter(name='myansrsourcebuhead').exists():
        if request.method == "GET":
            data = project_summary(project_id, show_header=False)
            return render(request, 'MyANSRSource/viewProjectSummary.html', data)
    else:
        raise PermissionDenied
