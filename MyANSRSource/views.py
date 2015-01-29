from templated_email import send_templated_mail
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
from django.contrib.formtools.wizard.views import SessionWizardView
from django.forms.formsets import formset_factory
from datetime import datetime, timedelta
from django.db.models import Q
from django.conf import settings

from MyANSRSource.models import Project, TimeSheetEntry, \
    ProjectMilestone, ProjectTeamMember, Book, ProjectChangeInfo, \
    Chapter, projectType

from MyANSRSource.forms import LoginForm, ProjectBasicInfoForm, \
    ProjectTeamForm, ProjectMilestoneForm, \
    ActivityForm, TimesheetFormset, ProjectFlagForm, \
    ChangeProjectBasicInfoForm, ChangeProjectTeamMemberForm, \
    ChangeProjectMilestoneForm, ChangeProjectForm, \
    CloseProjectMilestoneForm

# do not remove this import.  This is needed to initialize the app
from . import groupsupport

import CompanyMaster
from CompanyMaster import holidaycache
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
    tsFormset = createFormset(form=tsform, extra=2, initial=None,
                              prefix=None, delete=True)
    atFormset = createFormset(form=ActivityForm, extra=2, initial=None,
                              prefix=None, delete=True)
    # Initializing values
    days = ['monday', 'tuesday', 'wednesday', 'thursday',
            'friday', 'saturday', 'sunday']
    totallist = days
    totallist.append('total')
    leaveDayWork = False
    today = datetime.now().date()
    weekstartDate = today - timedelta(days=datetime.now().date().weekday())
    ansrEndDate = weekstartDate + timedelta(days=6)
    # Handler for form post
    if request.method == 'POST':
        # Getting the forms with submitted values
        timesheets = tsFormset(request.POST)
        activities = atFormset(request.POST, prefix='at')

        # Checking for form errors
        if timesheets.is_valid() and activities.is_valid():

            # Setting new start and end date
            changedStartDate = datetime.strptime(
                request.POST.get('startdate'), '%d%m%Y'
            ).date()
            changedEndDate = datetime.strptime(
                request.POST.get('enddate'), '%d%m%Y'
            ).date()

            # Initializing eachday total to 0
            totals = {"{0}{1}".format(eachDay, 'Total'): 0 for eachDay in days}
            totals['weekTotal'] = 0

            locationId = employee.models.Employee.objects.filter(
                user=request.user
            ).values('location')[0]['location']

            weekHolidays = Holiday.objects.filter(
                location=locationId,
                date__range=[changedStartDate, changedEndDate]
            ).values('date')

            for timesheet in timesheets.cleaned_data:
                # To check the form should be deleted or not
                if timesheet['DELETE'] is True:
                    deleteRecord(timesheet['tsId'])
                else:
                    for holiday in weekHolidays:
                        holidayDay = '{0}H'.format(
                            holiday['date'].strftime('%A').lower()
                        )
                        if timesheet[holidayDay] > 0:
                            leaveDayWork = True

                    # Calculates weekly total, daily total
                    totals = calculateTotals(totallist, timesheet,
                                             totals, activity=False)
            # Calculating billable total
            billableTotal = totals['weekTotal']

            for activity in activities.cleaned_data:
                # To check the form should be deleted or not
                if activity['DELETE'] is True:
                    deleteRecord(timesheet['atId'])
                else:
                    # Calculates weekly total, daily total
                    totals = calculateTotals(totallist, activity,
                                             totals, activity=True)
            # Calculating non-billable total
            nonbillableTotal = totals['weekTotal'] - billableTotal

            # Validations on various grounds based in weekly and daily totals
            hardWorkingDay = [
                eachTotal
                for eachTotal in
                totals
                if totals[eachTotal] > 24 and eachTotal !=
                'weekTotal']
            if len(hardWorkingDay):
                messages.error(request, 'You can only work for 24 hours a day')
            elif (totals['weekTotal'] < 36) | (totals['weekTotal'] > 44) | \
                 (billableTotal > 44) | (nonbillableTotal > 40) | \
                 (leaveDayWork is True):
                for eachActivity in activities.cleaned_data:
                    # A check to update or insert data
                    if eachActivity['atId'] > 0:
                        # Update Instance
                        nonbillableTS = TimeSheetEntry.objects.filter(
                            id=eachActivity['atId']
                        )[0]
                    else:
                        # Insert Instance
                        nonbillableTS = TimeSheetEntry()

                    saveUnApprovedTS(nonbillableTS, changedStartDate,
                                     changedEndDate, request.user,
                                     nonbillableTotal, days,
                                     eachActivity, hold=True, billable=False)

                # A check to update or insert data
                for eachTimesheet in timesheets.cleaned_data:
                    if eachTimesheet['tsId'] > 0:
                        billableTS = TimeSheetEntry.objects.filter(
                            id=eachTimesheet['tsId']
                        )[0]
                    else:
                        billableTS = TimeSheetEntry()

                    saveUnApprovedTS(billableTS, changedStartDate,
                                     changedEndDate, request.user,
                                     billableTotal, days,
                                     eachTimesheet, hold=True, billable=True)
            else:
                # Save Timesheet
                for eachActivity in activities.cleaned_data:
                    # Getting objects for models
                    if eachActivity['atId'] > 0:
                        nonbillableTS = TimeSheetEntry.objects.filter(
                            id=eachActivity['atId']
                        )[0]
                    else:
                        nonbillableTS = TimeSheetEntry()
                    # Common values for Billable and Non-Billable
                    saveApprovedTS(nonbillableTS, changedStartDate,
                                   changedEndDate, request.user,
                                   eachActivity, hold=True, billable=False)
                for eachTimesheet in timesheets.cleaned_data:
                    if eachTimesheet['tsId'] > 0:
                        billableTS = TimeSheetEntry.objects.filter(
                            id=eachTimesheet['tsId']
                        )[0]
                    else:
                        billableTS = TimeSheetEntry()
                    saveApprovedTS(nonbillableTS, changedStartDate,
                                   changedEndDate, request.user,
                                   eachActivity, hold=True, billable=True)
            return HttpResponseRedirect(request.get_full_path())
        else:
            # Handler for form errors
            returnValue = switchWeeks(request)
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
            tsFormset = createFormset(form=tsform, extra=0, initial=tsError,
                                      prefix=None, delete=True)
            atFormset = createFormset(form=ActivityForm, extra=0,
                                      initial=atError, prefix='at', delete=True)
            data = {'ErrorList': tsErrorList,
                    'shortDays': [eachDay.capitalize()[:3] for eachDay in days],
                    'hold': False,
                    'tsFormset': tsFormset,
                    'atFormset': atFormset}
            finalData = dict(returnValue.items() + data.items())
            return render(request, 'MyANSRSource/timesheetEntry.html',
                          finalData)
    else:
        # request.GET Method
        returnValue = switchWeeks(request)
        tsDataList = InitialUnApprovedTSList(weekstartDate, ansrEndDate,
                                             request.user, totallist,
                                             approved=False, project=True)
        atDataList = InitialUnApprovedTSList(weekstartDate, ansrEndDate,
                                             request.user, totallist,
                                             approved=False, project=False)
        if len(tsDataList):
            tsFormset = createFormset(form=tsform, extra=0, initial=tsDataList,
                                      prefix=None, delete=True)
            atFormset = createFormset(form=ActivityForm, extra=0,
                                      initial=atDataList, prefix='at',
                                      delete=True)
        else:
            tsFormset = createFormset(form=tsform, extra=2, initial=None,
                                      prefix=None, delete=True)
            atFormset = createFormset(form=ActivityForm, extra=2,
                                      initial=None, prefix='at',
                                      delete=True)
        tsApprovedDataList = ApprovedTSList(weekstartDate, ansrEndDate,
                                            request.user, totallist,
                                            approved=True, project=True)
        atApprovedDataList = ApprovedTSList(weekstartDate, ansrEndDate,
                                            request.user, totallist,
                                            approved=True, project=False)
        totals = CalculateSummary(weekstartDate, ansrEndDate, request.user)
        if len(tsApprovedDataList):
            messages.success(request, 'Timesheet is approved for this week')
            data = {'weekstartDate': weekstartDate,
                    'weekendDate': ansrEndDate,
                    'currentTimesheet': tsApprovedDataList,
                    'currentActivity': atApprovedDataList
                    }
            return render(request, 'MyANSRSource/timesheetApproved.html', data)
        else:
            if len(tsDataList):
                hold = tsDataList[0]['hold']
                if hold is True:
                    messages.warning(request,
                                     'This timesheet is sent for approval \
                                     to your manager')
                else:
                    messages.warning(request,
                                     'Your manager kept this timesheet on hold, \
                                     please resubmit')
            else:
                hold = False
            data = {'tsFormset': tsFormset,
                    'hold': hold,
                    'shortDays': [eachDay.capitalize()[:3] for eachDay in days],
                    'atFormset': atFormset}
            finalData = dict(returnValue.items() + data.items() +
                             totals.items())
            return render(request, 'MyANSRSource/timesheetEntry.html',
                          finalData)


# Deletes a TS Record
def deleteRecord(recId):
        TimeSheetEntry.objects.get(id=recId).delete()
        return 1


# Function to calculate weekly and daily totals
def calculateTotals(totallist, timesheet, totals, activity):
    if activity is False:
        for anitem in totallist:
            if timesheet[anitem + 'H']:
                if anitem == 'total':
                    totals['weekTotal'] += timesheet['totalH']
                else:
                    totals[anitem + 'Total'] += timesheet[anitem + 'H']
    else:
        for anitem in totallist:
            if timesheet['activity_' + anitem]:
                if 'total' in anitem:
                    totals['weekTotal'] += timesheet['activity_total']
                else:
                    totals[anitem + 'Total'] += timesheet['activity_' + anitem]
    return totals


# Function to save UnApprovedTS to DB
def saveUnApprovedTS(*args, **argv):
    # Assigning UnApprovedTS items to DB
    args[0].wkstart = args[1]
    args[0].wkend = args[2]
    args[0].teamMember = args[3]
    args[0].hold = argv['hold']
    args[0].exception = '10% deviation in totalhours for this week'
    if args[4] > 40:
        args[0].exception = 'Activity more than 40 Hours'
    # Assigning eachday values to DB
    for k, v in args[6].iteritems():
        if argv['billable']:
            setattr(args[0], k, v)
        else:
            for eachDay in args[5]:
                if k == 'activity_{0}'.format(eachDay):
                    variable = "{0}.{1}H".format(
                        args[0],
                        eachDay)
                    variable = variable.replace(' object', '')
                    exec("%s = %d" % (variable, v))
            if k == 'activity_total':
                args[0].totalH = v
            if k == 'activity_feedback':
                args[0].feedback = v
            if k == 'activity':
                args[0].activity = v
    args[0].save()
    return 1


# Function to save Approved TS to DB
def saveApprovedTS(*args, **argv):
    # Assigning ApprovedTS items to DB
    args[0].wkstart = args[1]
    args[0].wkend = args[2]
    args[0].teamMember = args[3]
    args[0].hold = argv['hold']
    args[0].approved = True
    args[0].approvedon = datetime.now()
    if argv['billable']:
        args[0].billable = True
    for k, v in args[4].iteritems():
        setattr(args[0], k, v)
    args[0].save()
    return 1


# Function to change the weekstart and weekend date
def switchWeeks(request):
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
        weekstartDate = datetime.strptime(
            request.GET.get('startdate'), '%d%m%Y'
        ).date() + timedelta(days=7)
        ansrEndDate = datetime.strptime(
            request.GET.get('enddate'), '%d%m%Y'
        ).date() + timedelta(days=7)
        disabled = 'next'
    else:
        disabled = 'next'
        today = datetime.now().date()
        weekstartDate = today - timedelta(days=datetime.now().date().weekday())
        ansrEndDate = weekstartDate + timedelta(days=6)
    returnValue = {'weekstartDate': weekstartDate,
                   'ansrEndDate': ansrEndDate,
                   'disabled': disabled}
    return returnValue


# Function to create formset based on number of forms, initial data
def createFormset(**argv):
    ff = formset_factory(argv['form'], extra=argv['extra'],
                         can_delete=argv['delete'])
    if argv['initial'] is not None:
        if argv['prefix'] is not None:
            ff = ff(prefix=argv['prefix'], initial=argv['initial'])
        else:
            ff = ff(initial=argv['initial'])
    elif argv['prefix'] is not None:
        ff = ff(prefix=argv['prefix'])
    return ff


# Function to get the form data from DB if TS is UnApproved
def InitialUnApprovedTSList(*args, **argv):
    Cvalue = ["{0}{1}".format(eachList, 'H') for eachList in args[3]]
    Cvalue.extend(['id', 'managerFeedback'])
    if argv['project']:
        qValues = ["{0}{1}".format(eachList, 'Q') for eachList in args[3]]
        Cvalue.extend(['id', 'project', 'location', 'hold',
                      'chapter', 'task', 'project__projectType'])
        Cvalue.extend(qValues)
        project = True
    else:
        Cvalue.append('activity')
        project = False
    fetchData = TimeSheetEntry.objects.filter(
        Q(
            wkstart=args[0],
            wkend=args[1],
            teamMember=args[2],
            approved=argv['approved'],
            project__isnull=project
        )).values(*Cvalue)
    return CreateDataList(fetchData, args[3], project=argv['project'])


# Function to get the form data from DB if TS is Approved
def ApprovedTSList(*args, **argv):
    Cvalue = ["{0}{1}".format(eachList, 'H') for eachList in args[3]]
    Cvalue.append('managerFeedback')
    if argv['project']:
        Cvalue.extend(['project__name', 'location__name',
                      'chapter__name', 'task'])
        project = True
    else:
        Cvalue.append('activity')
        project = False
    fetchData = TimeSheetEntry.objects.filter(
        Q(
            wkstart=args[0],
            wkend=args[1],
            teamMember=args[2],
            approved=argv['approved'],
            project__isnull=project
        )).values(*Cvalue)
    return fetchData


# Function to create a dataList
def CreateDataList(*args, **argv):
    tsData, tsDataList = {}, []
    for eachData in args[0]:
        for k, v in eachData.iteritems():
            if k == 'managerFeedback':
                tsData['feedback'] = v
            if argv['project']:
                tsData[k] = v
                if k == 'id':
                    tsData['tsId'] = v
                if k == 'project__projectType':
                    tsData['projectType'] = v
            else:
                if k == 'id':
                    tsData['atId'] = v
                for eachList in args[1]:
                    if eachList in k:
                        tsData['activity_' + eachList] = v
            tsDataList.append(tsData.copy())
            tsData.clear()
    return tsDataList


# Function to calculate summary totals
def CalculateSummary(*args):
    billableHours = TimeSheetEntry.objects.filter(
        Q(
            wkstart=args[0],
            wkend=args[1],
            teamMember=args[2],
            approved=False,
            activity__isnull=True
        ),
        ~Q(task='I')
    ).values('totalH')
    idleHours = TimeSheetEntry.objects.filter(
        Q(
            wkstart=args[0],
            wkend=args[1],
            task='I',
            teamMember=args[2],
            approved=False,
            activity__isnull=True
        ),
    ).values('totalH')
    othersHours = TimeSheetEntry.objects.filter(
        Q(
            wkstart=args[0],
            wkend=args[1],
            teamMember=args[2],
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
    return {'bTotal': bTotal, 'idleTotal': idleTotal,
            'othersTotal': othersTotal, 'idleHours': idleHours,
            'billableHours': billableHours}


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
    totalActiveProjects = Project.objects.filter(
        projectManager=request.user,
        closed=False
    ).count() if request.user.has_perm('MyANSRSource.manage_project') else 0

    unApprovedTimeSheet = TimeSheetEntry.objects.filter(
        project__projectManager=request.user,
        approved=False
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

    # Find the right holidays
    locationId = employee.models.Employee.objects.filter(
        user=request.user
    ).values('location')[0]['location']
    holidayList = Holiday.objects.filter(
        location=locationId
    ).values('name', 'date')
    for eachHoliday in holidayList:
        eachHoliday['date'] = eachHoliday['date'].strftime('%Y-%m-%d')
    data = {
        'username': request.session['username'],
        'firstname': request.session['firstname'],
        'TSProjectsCount': TSProjectsCount,
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
    try:
        user = authenticate(username=userName, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                if user.has_perm('MyANSRSource.enter_timesheet'):
                    request.session['username'] = userName
                    request.session['firstname'] = user.first_name
                    return HttpResponseRedirect('dashboard')
                else:
                    # We have an unknow group
                    messages.error(
                        request,
                        'This user does not have access to timesheets.')
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
                'Invalid userid & password / User could not be found on \
                Active Directory.')
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
            locationId = employee.models.Employee.objects.filter(
                user=self.request.user
            ).values('location')[0]['location']
            holidays = Holiday.objects.filter(
                location=locationId
            ).values('name', 'date')
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
                    readonlyfields = (
                        'member',
                        'role',
                        'startDate',
                        'endDate',
                        'rate',
                        'plannedEffort',
                        )
                    for fieldname in readonlyfields:
                        for eachForm in form:
                            eachForm.fields[fieldname].widget.attrs[
                                'readonly'
                            ] = 'True'

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
                'endDate'
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
        if self.request.session['changed'] is True:
            data = UpdateProjectInfo([form.cleaned_data for form in form_list])
            return render(
                self.request,
                'MyANSRSource/changeProjectId.html',
                data)
        else:
            return render(
                self.request,
                'MyANSRSource/NochangeProject.html',
                {})


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
            c = {}
            for eachForm in form:
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
                    for t in form.cleaned_data:
                        totalRate += t['amount']
                    for eachForm in form:
                        if float(projectTotal) != totalRate:
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
                milestoneDate = 'milestoneDate-{0}'.format(
                    milestoneDataCounter)
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
        pType = projectType.objects.get(
            description=request.POST.get('projectType'))
        pr.projectType = pType
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
        customerCode = CompanyMaster.models.Customer.objects.filter(
            id=request.session['customer']
        ).values('customerCode')[0]['customerCode']
        seqNumber = CompanyMaster.models.Customer.objects.filter(
            id=request.session['customer']
        ).values('seqNumber')[0]['seqNumber']
        seqNumber = seqNumber + 1
        cm = CompanyMaster.models.Customer.objects.get(
            id=request.session['customer']
        )
        cm.seqNumber = seqNumber
        cm.save()
        pr.customer = CompanyMaster.models.Customer.objects.filter(
            id=request.session['customer']
        )[0]
        pr.book = Book.objects.filter(id=request.session['book'])[0]
        pr.save()
        request.session['currentProject'] = pr.id
        request.session['currentProjectName'] = pr.name

        projectIdPrefix = "{0}_{1}_{2}".format(
            customerCode,
            datetime.now().year,
            str(seqNumber).zfill(4)
        )
        pru = Project.objects.get(id=pr.id)
        pru.projectId = "{0}".format(projectIdPrefix)
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


@login_required
def WrappedCreateProjectView(request):
    return createProject(request)


@login_required
def notify(request):
    projectId = request.session['currentProject']

    projectDetails = Project.objects.filter(
        id=projectId,
    ).values('startDate', 'projectManager')

    projectHead = CompanyMaster.models.Customer.objects.filter(
        id=request.session['customer'],
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
                    'pmname': projectDetails['projectManager'],
                    'startDate': projectDetails['startDate']
                    },
            )

    teamMembers = ProjectTeamMember.objects.filter(
        project=projectId
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
                    'pmname': projectDetails['projectManager'],
                    'startDate': projectDetails['startDate'],
                    'mystartdate': eachMember['startDate']
                    },
            )

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
        'project__projectType__code',
        'project__projectType__description'
    ).filter(project__closed=False)
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


createProject = CreateProjectWizard.as_view(FORMS)
