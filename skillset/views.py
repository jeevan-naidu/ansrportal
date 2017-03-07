from django.shortcuts import render, HttpResponse
from django.views.generic import View
from django.shortcuts import render
from django.utils import timezone
from employee.models import Employee, Designation, EmployeeCompanyInformation
from CompanyMaster.models import Department
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import timedelta
from datetime import date
from models import Skill_Lists, User_Skills
import xlwt


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
        department = Department.objects.all()
        reportee_list = Employee.objects.all()
        lists = []
        user_details = {'name': '', 'deisgnation': '', 'department': '', 'id': '', 'doj': '', 'skills': ''}
        for reportee in reportee_list:
            # import ipdb;
            # ipdb.set_trace()
            assert isinstance(reportee, object)
            try:
                skills = User_Skills.objects.filter(employee_id=reportee.employee_assigned_id)
            except User_Skills.DoesNotExist:
                skills = ''
            dept = EmployeeCompanyInformation.objects.filter(employee_id=reportee.employee_assigned_id).values(
                'department')
            for val in dept:
                dept = val['department']
            dept = Department.objects.filter(id=dept).values('name')
            if not dept:
                dept = ''
            for val in dept:
                dept = val['name']
            if not dept:
                dept = ''
            user_details['name'] = reportee.user.first_name + ' ' + reportee.user.last_name
            user_details['designation'] = reportee.designation.name
            user_details['department'] = dept
            id = reportee.idcard
            user_details['id'] = id[:-1]
            user_details['doj'] = reportee.joined
            user_details['skills'] = skills
            if reportee.user.is_active == True:
                lists.append(user_details)
                user_details = {'name': '', 'deisgnation': '', 'department': '', 'id': '', 'doj': '', 'skills': ''}

        skills = User_Skills.objects.filter(employee_id=employee)

        return render(request, 'skillset.html',
                      {'lists': lists, 'designation_all': designation_all, 'department': department})


def dept(request):
    if request.method == 'GET':
        # from ipdb import set_trace
        # set_trace()
        designation_all = Designation.objects.all()
        department = Department.objects.all()
        dept = request.GET.get('value')
        dept_name = Department.objects.filter(name=dept)
        dept_id = Department.objects.filter(id=dept_name).values('id')
        reportee_list = EmployeeCompanyInformation.objects.filter(department=dept_id).values('employee')
        lists = []
        user_details = {'name': '', 'deisgnation': '', 'department': '', 'id': '', 'doj': '', 'skills': ''}
        for val in reportee_list:
            employee_id = val['employee']
            employee = Employee.objects.get(employee_assigned_id = employee_id)
            try:
                skills = User_Skills.objects.filter(employee_id=employee.employee_assigned_id)
            except User_Skills.DoesNotExist:
                skills = ''
            dept = EmployeeCompanyInformation.objects.filter(employee_id=employee.employee_assigned_id).values(
                'department')
            for val in dept:
                dept = val['department']
            dept = Department.objects.filter(id=dept).values('name')
            if not dept:
                dept = ''
            for val in dept:
                dept = val['name']
            if not dept:
                dept = ''
            user_details['name'] = employee.user.first_name + ' ' + employee.user.last_name
            user_details['designation'] = employee.designation.name
            user_details['department'] = dept
            id = employee.idcard
            user_details['id'] = id[:-1]
            user_details['doj'] = employee.joined
            user_details['skills'] = skills
            if employee.user.is_active == True:
                lists.append(user_details)
                user_details = {'name': '', 'deisgnation': '', 'department': '', 'id': '', 'doj': '', 'skills': ''}

        return render(request, 'skillset.html',{'lists': lists,'department':department,'designation_all':designation_all})

def export_users_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Employee ID', 'Name', 'Department', 'Designation', 'Skills', 'Joining Date' ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = User.objects.all().values_list('username', 'first_name', 'last_name', 'email')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


