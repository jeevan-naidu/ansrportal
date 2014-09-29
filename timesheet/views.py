from django.contrib.auth import authenticate
from django.shortcuts import render
from django.http import HttpResponse
from timesheet.forms import LoginForm, ProjectMilestoneForm, \
    ProjectTeamForm, ProjectBasicInfoForm

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
            try:
                if user.groups.all()[0].name == "project manager":
                    return CreateProject(request)
                else:
                    return render(request, 'timesheet/timesheet.html')
            except IndexError:
                return HttpResponse("Sorry you dont have the permission \
                                    to get into projects")
        else:
            return HttpResponse("Logged in! Not Activated")
    else:
        return HttpResponse("Sorry no user is associated with this id")


def CreateProject(request):
    if request.method == 'POST':
        basicInfo = ProjectBasicInfoForm(request.POST)
        team = ProjectTeamForm(request.POST)
        milestone = ProjectMilestoneForm(request.POST)
        if basicInfo.is_valid() and team.is_valid() and milestone.is_valid():
            # Project Basic Information
            basicInfo.cleaned_data['name']
            basicInfo.cleaned_data['startDate']
            basicInfo.cleaned_data['endDate']
            basicInfo.cleaned_data['plannedEffort']
            basicInfo.cleaned_data['contingencyEffort']
            # Team Member and thier roles
            team.cleaned_data['role']
            team.cleaned_data['startDate']
            team.cleaned_data['plannedEffort']
            # Project Milestones
            milestone.cleaned_data['milestoneDate']
            milestone.cleaned_data['deliverables']
            milestone.cleaned_data['description']
    else:
        basicInfo = ProjectBasicInfoForm()
        team = ProjectTeamForm()
        milestone = ProjectMilestoneForm()
    data = {'basicInfo': basicInfo, 'team': team, 'milestone': milestone}
    return render(request, 'timesheet/manager.html', data)
