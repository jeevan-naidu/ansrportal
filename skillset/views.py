from django.shortcuts import render, HttpResponse
from django.views.generic import View
from django.shortcuts import render
from django.utils import timezone
from employee.models import Employee, Designation
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import timedelta
from datetime import date

# Create your views here.
def SkillSet(request):

    if request.method == 'GET':
        import ipdb;
        ipdb.set_trace()
        user = request.user
        employee = Employee.objects.get(user_id=user.id)
        designation_all = Designation.objects.all()
        id = employee.idcard
        name = user.first_name +" "+ user.last_name
        designation = employee.designation.name
        department = employee.business_unit
        doj = employee.joined
        return render(request, 'skillset.html',{'designation_all':designation_all,'id':id,'name':name,'designation':designation,'department':department,'doj':doj})