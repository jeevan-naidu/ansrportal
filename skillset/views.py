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

# def SkillSet(request):
#
#     if request.method == 'GET':
#         user = request.user
#         employee = Employee.objects.get(user_id=user.id)
#         designation_all = Designation.objects.all()
#         department  = Department.objects.all()
#         reportee_list = Employee.objects.filter(manager_id = employee.employee_assigned_id)
#         lists = []
#         user_details = {'name': '', 'deisgnation': '','department':department, 'id':'', 'doj':'', 'skills':''}
#         for reportee in reportee_list:
#             assert isinstance(reportee, object)
#             try:
#                 skills = User_Skills.objects.filter(employee_id=reportee.employee_assigned_id)
#             except User_Skills.DoesNotExist:
#                 skills = ''
#             user_details['name'] = reportee.user.first_name + ' ' + reportee.user.last_name
#             user_details['designation'] = reportee.designation.name
#             user_details['department'] = reportee.department.name
#             id = reportee.idcard
#             user_details['id'] = id[:-1]
#             user_details['doj'] = reportee.joined
#             user_details['skills'] = skills
#             if reportee.user.is_active == True:
#                 lists.append(user_details)
#                 user_details = {'name': '', 'deisgnation': '','department':department, 'id': '', 'doj': '', 'skills': ''}
#
#
#
#         skills = User_Skills.objects.filter(employee_id = employee)
#
#         return render(request, 'skillset.html',{'lists':lists,'designation_all':designation_all,'department':department})

def SkillSet(request):

    if request.method == 'GET':
        user = request.user
        employee = Employee.objects.get(user_id=user.id)
        designation_all = Designation.objects.all()
        department  = Department.objects.all()
        reportee_list = Employee.objects.all()
        lists = []
        user_details = {'name': '', 'deisgnation': '', 'id':'', 'doj':'', 'skills':''}
        for reportee in reportee_list:
            # import ipdb;
            # ipdb.set_trace()
            assert isinstance(reportee, object)
            try:
                skills = User_Skills.objects.filter(employee_id=reportee.employee_assigned_id)
            except User_Skills.DoesNotExist:
                skills = ''
            user_details['name'] = reportee.user.first_name + ' ' + reportee.user.last_name
            user_details['designation'] = reportee.designation.name
            # user_details['department'] = reportee.department.name
            id = reportee.idcard
            user_details['id'] = id[:-1]
            user_details['doj'] = reportee.joined
            user_details['skills'] = skills
            if reportee.user.is_active == True:
                lists.append(user_details)
                user_details = {'name': '', 'deisgnation': '','id': '', 'doj': '', 'skills': ''}



        skills = User_Skills.objects.filter(employee_id = employee)

        return render(request, 'skillset.html',{'lists':lists,'designation_all':designation_all,'department':department})
