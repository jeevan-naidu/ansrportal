from django.contrib.auth import authenticate, logout
from django.contrib import auth
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from timesheet.models import Project, TimeSheetEntry, ProjectChangeInfo, \
    ProjectMilestone, ProjectTeamMember
from timesheet.forms import LoginForm, ProjectMilestoneForm, \
    ProjectTeamForm, ProjectBasicInfoForm
from django.contrib.formtools.wizard.views import SessionWizardView
import logging
# views for ansr


def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return checkUser(
                form.cleaned_data['userid'],
                form.cleaned_data['password'],
                request)
    else:
        form = LoginForm()
    data = {'form': form}
    return render(request, 'timesheet/index.html', data)


def checkUser(userName, password, request):
    user = authenticate(username=userName, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            try:
                if user.groups.all()[0].name == "project manager":
                    return HttpResponseRedirect('login/createproject')
                else:
                    return render(request, 'timesheet/timesheet.html')
            except IndexError:
                return HttpResponse("Sorry you dont have the permission \
                                    to get into projects")
        else:
            return HttpResponse("Logged in! Not Activated")
    else:
        return HttpResponse("Sorry no user is associated with this id")


class CreateProjectWizard(SessionWizardView):
    template_name = "manager.html"

    def process_step(self, formdata):
        return super(CreateProjectWizard, self).process_step(formdata)

    def done(self, form_list, **kwargs):
        pr = Project()
        pr.name =  [form.cleaned_data.get('name') for form in form_list][0]
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
        return HttpResponse("Saved!!!")


def Logout(request):

    logout(request)
    request.session.flush()
    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
    return HttpResponseRedirect('/login')
