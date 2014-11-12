from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from employee.forms import LoginForm 
from employee.models import EmpBasic, EmpAddress
# Create your views here.
def logincred(request):
    if request.method =='GET':
        form = LoginForm()
        return render(request, 'login.html',{'form':form, })
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    ldapuserprofile = EmpBasic.objects.get(uid=request.user.username)
                    return HttpResponse("sucessfully login")
                else:
                    return HttpResponse("Your account is disabled")
            else:
                print "invalid login details: {0}, {1}".format(username, password)
                return HttpResponse("Invalid login details supplied.")
        else:
            return render(request, 'login.html', {
                'form': form,
        })
