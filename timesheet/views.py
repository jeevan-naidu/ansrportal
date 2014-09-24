from django.contrib.auth import authenticate
from django.shortcuts import render
from django.http import HttpResponse

# views for ansr


def index(request):
    return render(request, 'timesheet/index.html')


def checkUser(request):
    userName = request.POST.get('userName')
    passKey = request.POST.get('passKey')
    user = authenticate(username=userName, password=passKey)
    if user is not None:
        if user.is_active:
            return HttpResponse("Logged in! Activated")
        else:
            return HttpResponse("Logged in! Not Activated")
    else:
        return HttpResponse("No account matched")
