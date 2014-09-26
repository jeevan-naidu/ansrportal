from django.contrib.auth import authenticate
from django.shortcuts import render
from django.http import HttpResponse
from timesheet.forms import createProjectForm

# views for ansr


def index(request):
    return render(request, 'timesheet/index.html')


def checkUser(request):
    userName = request.POST.get('userName')
    passKey = request.POST.get('passKey')
    user = authenticate(username=userName, password=passKey)
    if user is not None:
        if user.is_active:
            try:
                if user.groups.all()[0].name == "project manager":
                    return render(request, 'timesheet/manager.html')
                else:
                    return render(request, 'timesheet/timesheet.html')
            except IndexError:
                return HttpResponse("Sorry you dont have the permission \
                                    to get into projects")
        else:
            return HttpResponse("Logged in! Not Activated")
    else:
        return HttpResponse("Sorry no user is associated with this id")


def addProject(request):
    if request.method == 'POST':
        form = createProjectForm(request.POST)
    else:
        form = createProjectForm()
    data = {'form': form}
    return render_to_response('timesheet/manager.html', data, \
                              context_instance=RequestContext(request))
