from django.contrib.auth import authenticate, logout
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from timesheet.models import Project, TimeSheetEntry, ProjectChangeInfo, \
    ProjectMilestone, ProjectTeamMember
from timesheet.forms import LoginForm, ProjectMilestoneForm, \
    ProjectTeamForm, ProjectBasicInfoForm
from django.contrib.formtools.wizard.views import SessionWizardView
# views for ansr


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
    data = {'form' : form if form else LoginForm(request.POST), }
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


class CreateProjectWizard(SessionWizardView):
    template_name = "manager.html"

    def process_step(self, formdata):
        return super(CreateProjectWizard, self).process_step(formdata)

    def done(self, form_list, **kwargs):
        pr = Project()
        pr.name = [form.cleaned_data.get('name') for form in form_list][0]
        pr.startDate = [form.cleaned_data.get(
            'startDate'
        ) for form in form_list][0]
        pr.endDate = [form.cleaned_data.get(
            'endDate'
        ) for form in form_list][0]
        pr.plannedEffort = [form.cleaned_data.get(
            'plannedEffort'
        ) for form in form_list][0]
        pr.contingencyEffort = [form.cleaned_data.get(
            'contingencyEffort'
        ) for form in form_list][0]
        pr.projectManager = self.request.user
        pr.save()

        ptm = ProjectTeamMember()
        ptm.project = Project.objects.get(
            name__exact=[form.cleaned_data.get('name')
                         for form in form_list][0]
        )
        ptm.member = User.objects.get(
            username__exact=[form.cleaned_data.get(
                'member'
            ) for form in form_list][1]
        )
        ptm.role = [form.cleaned_data.get('role') for form in form_list][1]
        ptm.startDate = [form.cleaned_data.get(
            'startDate'
        ) for form in form_list][1]
        ptm.plannedEffort = [form.cleaned_data.get(
            'plannedEffort'
        ) for form in form_list][1]
        ptm.save()

        pms = ProjectMilestone()
        pms.project = Project.objects.get(
            name__exact=[form.cleaned_data.get('name') for form in form_list][0]
        )
        pms.milestoneDate = [form.cleaned_data.get(
            'milestoneDate'
        ) for form in form_list][2]
        pms.deliverables = [form.cleaned_data.get(
            'deliverables'
        ) for form in form_list][2]
        pms.description = [form.cleaned_data.get(
            'description'
        ) for form in form_list][2]
        pms.save()
        return HttpResponse("Saved!!!")


def Logout(request):

    logout(request)
    request.session.flush()
    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
    return HttpResponseRedirect('/login')
