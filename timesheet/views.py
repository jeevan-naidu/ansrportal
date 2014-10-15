from django.contrib.auth import authenticate, logout
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from timesheet.models import Project, TimeSheetEntry, ProjectChangeInfo, \
    ProjectMilestone, ProjectTeamMember
from timesheet.forms import LoginForm, ProjectBasicInfoForm, \
    ProjectTeamForm, ProjectMilestoneForm
from django.contrib.formtools.wizard.views import SessionWizardView
from django.forms.formsets import formset_factory
# views for ansr

FORMS = [
    ("Define Project", ProjectBasicInfoForm),
    ("teamForm", formset_factory(ProjectTeamForm, extra=2)),
    ("milestoneForm", formset_factory(ProjectMilestoneForm, extra=2))
]


TEMPLATES = {
    "Define Project": "timesheet/manager.html",
    "teamForm": "timesheet/teamMember.html",
    "milestoneForm": "timesheet/milestone.html",
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


class CreateProjectWizard(SessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        pr = Project()
        for form in form_list:
            for k, v in [
                form.cleaned_data for form in form_list
            ][0].iteritems():
                setattr(pr, k, v)
        pr.projectManager = self.request.user
        pr.save()

        ptm = ProjectTeamMember()
        ptm.project = pr
        for memberData in [form.cleaned_data for form in form_list][1]:
            ptm.member = User.objects.get(id=memberData.get('member').id)
            for k, v in memberData.iteritems():
                setattr(ptm, k, v)
        ptm.save()

        pms = ProjectMilestone()
        pms.project = pr
        for milestoneData in [form.cleaned_data for form in form_list][2]:
            for k, v in milestoneData.iteritems():
                setattr(pms, k, v)
        pms.save()
        return HttpResponse("Saved!!!")


def Logout(request):

    logout(request)
    request.session.flush()
    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
    return HttpResponseRedirect('/timesheet')
