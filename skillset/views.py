from django.shortcuts import render, HttpResponse
from django.views.generic import View
from django.shortcuts import render
from django.utils import timezone
from employee.models import Employee, Designation
from CompanyMaster.models import Department
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import timedelta
from datetime import date
from models import Skill_Lists, User_Skills

# Create your views here.
# def SkillSet(request):

#     if request.method == 'GET':
#         # import ipdb;
#         # ipdb.set_trace()
#         user = request.user
#         employee = Employee.objects.get(user_id=user.id)
#         designation_all = Designation.objects.all()
#         department  = Department.objects.all()
#         skills = User_Skills.objects.filter(employee_id = employee)
#         id = employee.idcard
#         id = id[:-1]
#         name = user.first_name +" "+ user.last_name
#         designation = employee.designation.name
        
#         doj = employee.joined
#         return render(request, 'skillset.html',{'skills':skills,'designation_all':designation_all,
#             'id':id,'name':name,'designation':designation,'department':department,'doj':doj})

def SkillSet(request):

    if request.method == 'GET':
        import ipdb;
        ipdb.set_trace()
        user = request.user
        employee = Employee.objects.get(user_id=user.id)
        designation_all = Designation.objects.all()
        department  = Department.objects.all()
        users = Employee.objects.all()
        manager_filter = Employee.objects.filter(manager_id = user.manager_id)
        skills = User_Skills.objects.filter(employee_id = employee)
        id = employee.idcard
        id = id[:-1]
        name = user.first_name +" "+ user.last_name
        designation = employee.designation.name
        
        doj = employee.joined
        return render(request, 'skillset.html',{'skills':skills,'designation_all':designation_all,
            'id':id,'name':name,'designation':designation,'department':department,'doj':doj})
