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
        form = ProjectBasicInfoForm(request.POST)
        if form.is_valid():
            form.cleaned_data['name']
            form.cleaned_data['startDate']
            form.cleaned_data['endDate']
            form.cleaned_data['plannedEffort']
            form.cleaned_data['contingencyEffort']
    else:
        form = ProjectBasicInfoForm()
    data = {'form': form}
    return render(request, 'timesheet/manager.html', data)
