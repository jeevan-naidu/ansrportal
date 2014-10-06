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
        logging.error('Step executed')

    def done(self, form_list, **kwargs):
        logging.error('Done method called with {0}'.format(form_list))
        return HttpResponseRedirect("/login")


def process_form_data(request):

    if request.method == 'POST':
        basicInfo = ProjectBasicInfoForm(request.POST)
        team = ProjectTeamForm(request.POST)
        milestone = ProjectMilestoneForm(request.POST)
        # and team.is_valid() and milestone.is_valid():
        if basicInfo.is_valid():
            logging.error(basicInfo.cleaned_data['name'])
            # Project Basic Information
            pr = Project()
            pr.name = basicInfo.cleaned_data['name']
            pr.startDate = basicInfo.cleaned_data['startDate']
            pr.endDate = basicInfo.cleaned_data['endDate']
            pr.plannedEffort = basicInfo.cleaned_data['plannedEffort']
            pr.contingencyEffort = basicInfo.cleaned_data[
                'contingencyEffort'
            ]
            pr.projectManager = request.user
            pr.save()
            # Team Member and thier roles
            # team.cleaned_data['role']
            # team.cleaned_data['startDate']
            # team.cleaned_data['plannedEffort']
            # team.save()
            # Project Milestones
            # milestone.cleaned_data['milestoneDate']
            # milestone.cleaned_data['deliverables']
            # milestone.cleaned_data['description']
    else:
        basicInfo = ProjectBasicInfoForm()
        team = ProjectTeamForm()
        milestone = ProjectMilestoneForm()

    data = {'basicInfo': basicInfo, 'team': team, 'milestone': milestone}
    return render(request, 'timesheet/sucess.html', data)


def Logout(request):

    logout(request)
    request.session.flush()
    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
    return HttpResponseRedirect('/login')
