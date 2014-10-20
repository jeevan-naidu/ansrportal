from django.contrib.auth import authenticate, logout
from django.contrib import auth, messages
from django.shortcuts import render
from django.http import HttpResponseRedirect
from timesheet.models import Project, TimeSheetEntry, ProjectChangeInfo, \
    ProjectMilestone, ProjectTeamMember
from timesheet.forms import LoginForm, ProjectBasicInfoForm, \
    ProjectTeamForm, ProjectMilestoneForm
from django.contrib.formtools.wizard.views import SessionWizardView
from django.forms.formsets import formset_factory
from django.contrib.auth.models import User
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
    return render(request, 'timesheet/timesheet.html')


def checkUser(userName, password, request, form):
    user = authenticate(username=userName, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            try:
                if user.groups.all()[0].name == "project manager":
                    return HttpResponseRedirect('project/add')
            except IndexError:
                return HttpResponseRedirect('add')
        else:
            messages.error(request, 'Sorry this user is not active')
            return loginResponse(request, form, 'timesheet/index.html')
    else:
        messages.error(request, 'Sorry login failed')
        return loginResponse(request, form, 'timesheet/index.html')

def CreateProject(request):
    if request.method == 'POST':
        basicInfoForm = ProjectBasicInfoForm(request.POST)
        teamForm = ProjectTeamForm(request.POST)
        milestoneForm = ProjectMilestoneForm(request.POST)

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
        ).strftime('%Y-%m-%d')
        basicInfo['endDate'] = basicInfo.get(
            'endDate'
        ).strftime('%Y-%m-%d')

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
                id=request.POST.get(teamMemberId)
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
