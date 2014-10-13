from django.contrib.auth import authenticate, logout
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from timesheet.models import Project, TimeSheetEntry, ProjectChangeInfo, \
    ProjectMilestone, ProjectTeamMember
from timesheet.forms import *
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

        if basicInfoForm.is_valid() and teamForm.is_valid() \
                and milestoneForm.is_valid():
            return HttpResponse('Okay')
    else:
        basicInfoForm = ProjectBasicInfoForm()
        teamForm = ProjectTeamForm()
        milestoneForm = ProjectMilestoneForm()

    data = {
        'basicInfoForm': basicInfoForm,
        'teamForm': teamForm,
        'milestoneForm': milestoneForm
    }

    return render(request, 'timesheet/manager.html', data)

def Logout(request):
    logout(request)
    request.session.flush()
    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
    return HttpResponseRedirect('/timesheet')
