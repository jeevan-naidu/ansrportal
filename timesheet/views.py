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
# views for ansr

FORMS = [
    ("Define Project", ProjectBasicInfoForm),
    ("Add team members", formset_factory(
        ProjectTeamForm,
        extra=2,
        can_delete=True
    )),
    ("Define Milestones", formset_factory(
        ProjectMilestoneForm,
        extra=2,
        can_delete=True
    )),
]


TEMPLATES = {
    "Define Project": "timesheet/basicInfo.html",
    "Add team members": "timesheet/teamMember.html",
    "Define Milestones": "timesheet/milestone.html",
    "Validate": "timesheet/snapshot.html",
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
    # Getting the form values and storing it to DB.
    if request.method == 'POST':
        # Getting the forms with submitted values
        timesheets = tsFormset(request.POST)
        activities = atFormset(request.POST)
        # Getting objects for models
        billableTS = TimeSheetEntry()
        nonbillableTS = TimeSheetEntry()
        # Common values for Billable and Non-Billable
        nonbillableTS.wkstart = weekstartDate
        nonbillableTS.wkend = ansrEndDate
        nonbillableTS.teamMember = request.user
        billableTS.wkstart = weekstartDate
        billableTS.wkend = ansrEndDate
        billableTS.teamMember = request.user
        # User values for timsheet
        if timesheets.is_valid() and activities.is_valid():
            mondayTotal = 0
            tuesdayTotal = 0
            wednesdayTotal = 0
            thursdayTotal = 0
            fridayTotal = 0
            saturdayTotal = 0
            weekTotal = 0
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
                    setattr(billableTS, k, v)
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
                    setattr(nonbillableTS, k, v)
            if (mondayTotal > 24) | (tuesdayTotal > 24) | \
                    (wednesdayTotal > 24) | (thursdayTotal > 24) | \
                    (fridayTotal > 24) | (saturdayTotal > 24):
                messages.error(request, 'You can only work for 24 hours a day')
            elif (weekTotal < minAutoApprove) | (weekTotal > maxAutoApprove):
                billableTS.save()
                nonbillableTS.save()
                messages.info(
                    request,
                    'Timesheet is pending for this week'
                )
            else:
                # Save Timesheet
                billableTS.approved = True
                billableTS.approvedon = datetime.now()
                nonbillableTS.approved = True
                nonbillableTS.approvedon = datetime.now()
                billableTS.save()
                nonbillableTS.save()
                messages.success(
                    request,
                    'Timesheet is approved for this week'
                )
        return HttpResponseRedirect('/timesheet/entry')
    else:
        # Creating data for templates
        data = {'weekstartDate': weekstartDate,
                'weekendDate': ansrEndDate,
                'tsFormset': tsFormset,
                'atFormset': atFormset}
        return render(request, 'timesheet/timesheet.html', data)


def checkUser(userName, password, request, form):
    user = authenticate(username=userName, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            try:
                if user.groups.all()[0].name == "project manager":
                    return HttpResponseRedirect('project/add')
                elif user.groups.all()[0].name == "project team":
                    return HttpResponseRedirect('entry')
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
        basicInfo['startDate'] = basicInfo.get(
            'startDate'
        ).strftime('%Y-%m-%d %H:%M%z')
        basicInfo['endDate'] = basicInfo.get(
            'endDate'
        ).strftime('%Y-%m-%d %H:%M%z')
        print [form.cleaned_data for form in form_list][1]
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
        return render(self.request, 'timesheet/snapshot.html', data)


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
        return render(request, 'timesheet/success.html', data)


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
