from django.contrib.auth import authenticate, logout
from django.contrib import auth, messages
from django.shortcuts import render
from django.http import HttpResponseRedirect
from timesheet.models import Project, TimeSheetEntry, \
    ProjectMilestone, ProjectTeamMember
from timesheet.forms import LoginForm, ProjectBasicInfoForm, \
    ProjectTeamForm, ProjectMilestoneForm, \
    ActivityForm, TimesheetFormset
from django.contrib.formtools.wizard.views import SessionWizardView
from django.forms.formsets import formset_factory
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.db.models import Q
# views for ansr

FORMS = [
    ("Define Project", ProjectBasicInfoForm),
    ("Add team members", formset_factory(
        ProjectTeamForm,
        extra=2,
        can_delete=True
    )),
    ("Financial Milestones", formset_factory(
        ProjectMilestoneForm,
        extra=2,
        can_delete=True
    )),
]


TEMPLATES = {
    "Define Project": "timesheet/projectBasicInfo.html",
    "Add team members": "timesheet/projectTeamMember.html",
    "Financial Milestones": "timesheet/projectMilestone.html",
    "Validate": "timesheet/projectSnapshot.html",
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
    return loginResponse(request, form, 'timesheet/index.html')


def loginResponse(request, form, template):
    data = {'form': form if form else LoginForm(request.POST), }
    return render(request, template, data)


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
    weekstartDate = today - timedelta(days=datetime.now().date().weekday())
    ansrEndDate = weekstartDate + timedelta(days=5)
    disabled = 'next'
    # Getting the form values and storing it to DB.
    if request.method == 'POST':
        # Getting the forms with submitted values
        timesheets = tsFormset(request.POST)
        activities = atFormset(request.POST)
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
            weekTotal = 0
            (timesheetList, activitiesList,
             timesheetDict, activityDict) = ([], [], {}, {})
            for timesheet in timesheets:
                del(timesheet.cleaned_data['DELETE'])
                for k, v in timesheet.cleaned_data.iteritems():
                    if k == 'monday':
                        mondayTotal += v
                    elif k == 'tuesday':
                        tuesdayTotal += v
                    elif k == 'wednesday':
                        wednesdayTotal += v
                    elif k == 'thursday':
                        thursdayTotal += v
                    elif k == 'friday':
                        fridayTotal += v
                    elif k == 'saturday':
                        saturdayTotal += v
                    elif k == 'total':
                        weekTotal += v
                    timesheetDict[k] = v
                timesheetList.append(timesheetDict.copy())
                timesheetDict.clear()
            for activity in activities:
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
                    elif k == 'total':
                        weekTotal += v
                    activityDict[k] = v
                activitiesList.append(activityDict.copy())
                activityDict.clear()
            if (mondayTotal > 24) | (tuesdayTotal > 24) | \
                    (wednesdayTotal > 24) | (thursdayTotal > 24) | \
                    (fridayTotal > 24) | (saturdayTotal > 24):
                messages.error(request, 'You can only work for 24 hours a day')
            elif (weekTotal < minAutoApprove) | (weekTotal > maxAutoApprove):
                for eachActivity in activitiesList:
                    # Getting objects for models
                    nonbillableTS = TimeSheetEntry()
                    # Common values for Billable and Non-Billable
                    nonbillableTS.wkstart = changedStartDate
                    nonbillableTS.wkend = changedEndDate
                    nonbillableTS.teamMember = request.user
                    for k, v in eachActivity.iteritems():
                        if k == 'activity_monday':
                            nonbillableTS.monday = v
                        elif k == 'activity_tuesday':
                            nonbillableTS.tuesday = v
                        elif k == 'activity_wednesday':
                            nonbillableTS.wednesday = v
                        elif k == 'activity_thursday':
                            nonbillableTS.thursday = v
                        elif k == 'activity_friday':
                            nonbillableTS.friday = v
                        elif k == 'activity_saturday':
                            nonbillableTS.saturday = v
                        elif k == 'activity_total':
                            nonbillableTS.total = v
                        elif k == 'activity_feedback':
                            nonbillableTS.feedback = v
                        elif k == 'activity':
                            nonbillableTS.activity = v
                    nonbillableTS.save()
                for eachTimesheet in timesheetList:
                    billableTS = TimeSheetEntry()
                    billableTS.wkstart = changedStartDate
                    billableTS.wkend = changedEndDate
                    billableTS.teamMember = request.user
                    for k, v in eachTimesheet.iteritems():
                        setattr(billableTS, k, v)
                    billableTS.save()
                messages.info(
                    request,
                    'Timesheet is pending for approval this week'
                )
            else:
                # Save Timesheet
                for eachActivity in activitiesList:
                    # Getting objects for models
                    nonbillableTS = TimeSheetEntry()
                    # Common values for Billable and Non-Billable
                    nonbillableTS.wkstart = changedStartDate
                    nonbillableTS.wkend = changedEndDate
                    nonbillableTS.activity = activity
                    nonbillableTS.teamMember = request.user
                    nonbillableTS.approved = True
                    nonbillableTS.approvedon = datetime.now()
                    for k, v in eachActivity.iteritems():
                        setattr(nonbillableTS, k, v)
                    nonbillableTS.save()
                for eachTimesheet in timesheetList:
                    billableTS = TimeSheetEntry()
                    billableTS.wkstart = changedStartDate
                    billableTS.wkend = changedEndDate
                    billableTS.teamMember = request.user
                    billableTS.approved = True
                    billableTS.approvedon = datetime.now()
                    for k, v in eachTimesheet.iteritems():
                        setattr(billableTS, k, v)
                    billableTS.save()
                messages.success(
                    request,
                    'Timesheet is approved for this week'
                )
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
        # Creating data for templates
        cwTimesheet = TimeSheetEntry.objects.filter(
            wkstart=weekstartDate, wkend=ansrEndDate,
            teamMember=request.user,
            approved=False
        ).count()
        cwActivityData = TimeSheetEntry.objects.filter(
            Q(
                wkstart=weekstartDate,
                wkend=ansrEndDate,
                teamMember=request.user,
                approved=False,
                project__isnull=True
            )
        ).values('activity', 'mondayH', 'tuesdayH', 'wednesdayH', 'thursdayH',
                 'fridayH', 'saturdayH', 'totalH', 'managerFeedback'
                 )
        cwTimesheetData = TimeSheetEntry.objects.filter(
            Q(
                wkstart=weekstartDate,
                wkend=ansrEndDate,
                teamMember=request.user,
                approved=False,
                activity__isnull=True
            )
        ).values('project', 'chapter', 'task', 'mondayH',
                 'tuesdayH', 'wednesdayH', 'thursdayH',
                 'fridayH', 'saturdayH', 'totalH', 'managerFeedback'
                 )
        tsData = {}
        tsDataList = []
        for eachData in cwTimesheetData:
            for k, v in eachData.iteritems():
                tsData[k] = v
                if k == 'managerFeedback':
                    tsData['feedback'] = v
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
                if 'total' in k:
                    atData['activity_total'] = v
                if k == 'managerFeedback':
                    atData['feedback'] = v
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
            atFormset = atFormset(initial=atDataList)
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
                 'fridayH', 'saturdayH', 'totalH', 'managerFeedback'
                 )
        cwApprovedTimesheetData = TimeSheetEntry.objects.filter(
            Q(
                wkstart=weekstartDate,
                wkend=ansrEndDate,
                teamMember=request.user,
                approved=True,
                activity__isnull=True
            )
        ).values('project__name', 'chapter__name', 'mondayH',
                 'tuesdayH', 'wednesdayH', 'thursdayH', 'task',
                 'fridayH', 'saturdayH', 'totalH', 'managerFeedback'
                 )
        if cwApprovedTimesheet > 0:
            messages.success(request, 'Timesheet is approved for this week')
            data = {'weekstartDate': weekstartDate,
                    'weekendDate': ansrEndDate,
                    'disabled': disabled,
                    'currentTimesheet': cwApprovedTimesheetData,
                    'currentActivity': cwApprovedActivityData
                    }
            return render(request, 'timesheet/timesheetApproved.html', data)
        else:
            if cwTimesheet > 0:
                messages.warning(request,
                                 'Timesheet is Pending for approval this week')
            else:
                messages.info(request,
                              'Please fill timesheet for this week')
            data = {'weekstartDate': weekstartDate,
                    'weekendDate': ansrEndDate,
                    'disabled': disabled,
                    'tsFormset': tsFormset,
                    'atFormset': atFormset}
            return render(request, 'timesheet/timesheetEntry.html', data)


def ApproveTimesheet(request):
    return render(request, 'timesheet/timesheetApprove.html', {})


def Dashboard(request):
    if request.session['usertype'] == 'pm':
        totalActiveProjects = Project.objects.filter(
            projectManager=request.user
        ).count()
        unApprovedTimeSheet = TimeSheetEntry.objects.filter(
            project__projectManager=request.user,
            approved=False
        ).count()
        totalEmployees = User.objects.all().count()
    else:
        totalActiveProjects = 0
        unApprovedTimeSheet = 0
        totalEmployees = 0
    data = {
        'username': request.session['username'],
        'usertype': request.session['usertype'],
        'activeProjects': totalActiveProjects,
        'unapprovedts': unApprovedTimeSheet,
        'totalemp': totalEmployees
    }
    return render(request, 'timesheet/landingPage.html', data)


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
                return loginResponse(request, form, 'timesheet/index.html')
        else:
            messages.error(request, 'Sorry this user is not active')
            return loginResponse(request, form, 'timesheet/index.html')
    else:
        messages.error(request, 'Sorry login failed')
        return loginResponse(request, form, 'timesheet/index.html')


class CreateProjectWizard(SessionWizardView):

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        teamDataCounter = 0
        milestoneDataCounter = 0
        changedTeamData = {}
        changedMilestoneData = {}
        cleanedTeamData = []
        cleanedMilestoneData = []

        basicInfo = [form.cleaned_data for form in form_list][0]
        chapterList = []
        for eachChapter in basicInfo['chapters']:
            chapterList.append(eachChapter.id)
        self.request.session['chapters'] = chapterList
        basicInfo['startDate'] = basicInfo.get(
            'startDate'
        ).strftime('%Y-%m-%d %H:%M%z')
        basicInfo['endDate'] = basicInfo.get(
            'endDate'
        ).strftime('%Y-%m-%d %H:%M%z')
        for teamData in [form.cleaned_data for form in form_list][1]:
            teamDataCounter += 1
            for k, v in teamData.iteritems():
                k = "{0}-{1}".format(k, teamDataCounter)
                changedTeamData[k] = v
            startDate = 'startDate-{0}'.format(teamDataCounter)
            changedTeamData[startDate] = changedTeamData.get(
                startDate
            ).strftime('%Y-%m-%d')
            teamMemberId = 'teamMemberId-{0}'.format(teamDataCounter)
            member = 'member-{0}'.format(teamDataCounter)
            changedTeamData[teamMemberId] = changedTeamData.get(member).id
            DELETE = 'DELETE-{0}'.format(teamDataCounter)
            del changedTeamData[DELETE]
            self.request.session['totalMemberCount'] = teamDataCounter + 1
            cleanedTeamData.append(changedTeamData.copy())
            changedTeamData.clear()

        for milestoneData in [form.cleaned_data for form in form_list][2]:
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

        data = {
            'basicInfo': basicInfo,
            'teamMember': cleanedTeamData,
            'milestone': cleanedMilestoneData
        }
        return render(self.request, 'timesheet/projectSnapshot.html', data)


def saveProject(request):
    if request.method == 'POST':
        pr = Project()
        pr.name = request.POST.get('name')
        pr.startDate = request.POST.get('startDate')
        pr.endDate = request.POST.get('endDate')
        pr.plannedEffort = request.POST.get('plannedEffort')
        pr.contingencyEffort = request.POST.get('contingencyEffort')
        pr.projectManager = request.user
        pr.save()
        request.session['currentProject'] = pr.id

        for eachId in request.session['chapters']:
            pr.chapters.add(eachId)

        for memberCount in range(1, request.session['totalMemberCount']):
            ptm = ProjectTeamMember()
            ptm.project = pr
            teamMemberId = "teamMemberId-{0}".format(memberCount)
            role = "role-{0}".format(memberCount)
            plannedEffort = "plannedEffort-{0}".format(memberCount)
            startDate = "startDate-{0}".format(memberCount)

            ptm.member = User.objects.get(
                pk=request.POST.get(teamMemberId)
            )
            ptm.role = request.POST.get(role)
            ptm.plannedEffort = request.POST.get(plannedEffort)
            ptm.startDate = request.POST.get(startDate)
            ptm.save()

        for milestoneCount in range(1, request.session['totalMilestoneCount']):
            pms = ProjectMilestone()
            pms.project = pr
            milestoneDate = 'milestoneDate-{0}'.format(milestoneCount)
            description = 'description-{0}'.format(milestoneCount)
            deliverables = 'deliverables-{0}'.format(milestoneCount)
            pms.milestoneDate = request.POST.get(milestoneDate)
            pms.description = request.POST.get(description)
            pms.deliverables = request.POST.get(deliverables)
            pms.save()

        data = {'projectId': pr.id, 'projectName': pr.name}
        return render(request, 'timesheet/projectSuccess.html', data)


def notify(request):
    projectId = request.session['currentProject']
    teamMembers = User.objects.filter(
        username=ProjectTeamMember.objects.filter(project=projectId)
    )
    print teamMembers


def deleteProject(request):
    ProjectBasicInfoForm()
    ProjectTeamForm()
    ProjectMilestoneForm()
    return HttpResponseRedirect('add')


def Logout(request):
    logout(request)
    request.session.flush()
    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
    return HttpResponseRedirect('/timesheet')
