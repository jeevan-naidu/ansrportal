from django.shortcuts import render, HttpResponse
from django.views.generic import View
from django.shortcuts import render
from django.utils import timezone
from employee.models import Employee, Designation, EmployeeCompanyInformation
from CompanyMaster.models import Department, BusinessUnit
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import timedelta
from datetime import date
from models import Skill_Lists, User_Skills
import xlwt
from django.http import JsonResponse
import json
from Leave.forms import UserListViewForm

def SkillSet(request):
    if request.method == 'GET':
        form = UserListViewForm()
        user = request.user
        if request.user.groups.filter(name__in=['myansrsourceHR']).exists() or request.user.is_superuser == True:
            employee = Employee.objects.get(user_id=user.id)
            designation_all = Designation.objects.all()
            department = Department.objects.all()
            skills_all = Skill_Lists.objects.all()
            reportee = Employee.objects.all()
            lists = []
            user_details = {"name": "", "deisgnation": "", "department": "", "id": "", "doj": "", "skills": ""}
            for val in reportee:
                employee_id = val.employee_assigned_id
                employee = Employee.objects.get(employee_assigned_id=employee_id)
                try:
                    skillset = User_Skills.objects.filter(emp_mid=employee.employee_assigned_id).values('skills_name','skills_type')
                    skills_list = []
                    skills_dict = {'skills_name':'','skills_type':''}
                    for skill in skillset:
                        skills_dict['skills_name'] = skill['skills_name']
                        skills_dict['skills_type'] = skill['skills_type']
                        skills_list.append(skills_dict)
                        skills_dict = {'skills_name':'','skills_type':''}
                except User_Skills.DoesNotExist:
                    skills_list = None
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
                user_details['skills'] = skills_list
                if employee.user.is_active == True:
                    lists.append(user_details)
                    user_details = {"name": "", "deisgnation": "", "department": "", "id": "", "doj": "",  "skills": ""}


        elif request.user.groups.filter(name__in=['myansrsourcePM']).exists():
            employee = Employee.objects.get(user_id=user.id)
            designation_all = Designation.objects.all()
            department = Department.objects.all()
            skills_all = Skill_Lists.objects.all()
            mgrid = Employee.objects.get(user_id=request.user.id)
            reportee_business_unit = BusinessUnit.objects.filter(new_bu_head=mgrid.user_id)
            if not reportee_business_unit:
                reportee = Employee.objects.filter(manager_id=mgrid)
                lists = []
                user_details = {"name": "", "deisgnation": "", "department": "", "id": "", "doj": "", "skills": ""}
                for val in reportee:
                    employee_id = val.employee_assigned_id
                    employee = Employee.objects.get(employee_assigned_id=employee_id)
                    try:
                        skillset = User_Skills.objects.filter(emp_mid=employee.employee_assigned_id).values(
                            'skills_name', 'skills_type')
                        skills_list = []
                        skills_dict = {'skills_name': '', 'skills_type': ''}
                        for skill in skillset:
                            skills_dict['skills_name'] = skill['skills_name']
                            skills_dict['skills_type'] = skill['skills_type']
                            skills_list.append(skills_dict)
                            skills_dict = {'skills_name': '', 'skills_type': ''}
                    except User_Skills.DoesNotExist:
                        skills_list = None
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
                    user_details['skills'] = skills_list
                    if employee.user.is_active == True:
                        lists.append(user_details)
                        user_details = {"name": "", "deisgnation": "", "department": "", "id": "", "doj": "",
                                        "skills": ""}
            else:
                reportee = Employee.objects.filter(business_unit=reportee_business_unit)
                lists = []
                user_details = {"name": "", "deisgnation": "", "department": "", "id": "", "doj":"" , "skills": ""}
                for val in reportee:
                    employee_id = val.employee_assigned_id
                    employee = Employee.objects.get(employee_assigned_id=employee_id)
                    try:
                        skillset = User_Skills.objects.filter(emp_mid=employee.employee_assigned_id).values('skills_name','skills_type')
                        skills_list = []
                        skills_dict = {'skills_name':'','skills_type':''}
                        for skill in skillset:
                            skills_dict['skills_name'] = skill['skills_name']
                            skills_dict['skills_type'] = skill['skills_type']
                            skills_list.append(skills_dict)
                            skills_dict = {'skills_name':'','skills_type':''}
                    except User_Skills.DoesNotExist:
                        skills_list = None
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
                    user_details['skills'] = skills_list

                    if employee.user.is_active == True:
                        lists.append(user_details)
                        user_details = {"name": "", "deisgnation": "", "department": "", "id": "", "doj": "",  "skills": ""}
                jlistasa = []
                for sub in lists:
                    sub['name'] = str(sub['name'])
                    sub['designation'] = str(sub['designation'])
                    sub['department'] = str(sub['department'])
                    sub['id'] = str(sub['id'])
                    sub['doj'] = str(sub['doj'])
                    sub_list = []
                    for sub_skills in sub['skills']:
                        sub_skills['skills_name'] = str(sub_skills['skills_name'])
                        sub_skills['skills_type'] = str(sub_skills['skills_type'])
                        sub_list.append(sub_skills)
                    jlistasa.append(sub)
                json_list = json.dumps(jlistasa)
                count = len(lists)

                return render(request, 'skillset.html',
                              {'lists': lists, 'json_list': json_list, 'count': count, 'form': form,
                               'skills_all': skills_all, 'designation_all': designation_all, 'department': department})


        else:
            employee = Employee.objects.get(user_id=user.id)
            designation_all = Designation.objects.all()
            department = Department.objects.all()
            skills_all = Skill_Lists.objects.all()
            lists = []
            user_details = {"name": "", "deisgnation": "", "department": "", "id": "", "doj": "", "skills": ""}
            try:
                skills = User_Skills.objects.filter(emp_mid=employee.employee_assigned_id)
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
                user_details = {"name": "", "deisgnation": "", "department": "", "id": "", "doj": "", "skills": ""}

            return render(request, 'skillset.html',
                          {'lists': lists, 'designation_all': designation_all, 'department': department})

        jlistasa = []
        for sub in lists:
            sub['name'] = str(sub['name'])
            sub['designation'] = str(sub['designation'])
            sub['department'] = str(sub['department'])
            sub['id'] = str(sub['id'])
            sub['doj'] = str(sub['doj'])
            sub_list =[]
            for sub_skills in sub['skills']:
                sub_skills['skills_name'] = str(sub_skills['skills_name'])
                sub_skills['skills_type'] = str(sub_skills['skills_type'])
                sub_list.append(sub_skills)
            jlistasa.append(sub)
        json_list = json.dumps(jlistasa)
        count = len(lists)

        return render(request, 'skillset.html', {'lists':lists, 'json_list':json_list, 'count':count, 'form': form, 'skills_all': skills_all,
                                                 'designation_all': designation_all, 'department': department})

def dept(request):
    if request.method == 'GET':
        lists_dept = filters(request)
        return render(request, 'skillset.html', {'lists': lists_dept['lists'], 'department': lists_dept['department'],
                                                 'designation_all': lists_dept['designation_all']})

def designation(request):
    if request.method == 'GET':
        designation_all = Designation.objects.all()
        department = Department.objects.all()
        desg = request.GET.get('desg')
        reportee_list = Designation.objects.filter(name=desg).values('employee')
        for val in reportee_list:
            employee = val['employee']
        lists = []
        if not employee:
            data = ({'lists': lists, 'designation_all': designation_all, 'department': department})
            return data
        user_details = {"name": "", "deisgnation": "", "department": "", "id": "", "doj": "", "skills": ""}
        for val in reportee_list:
            employee_id = val['employee']
            try:
                employee = Employee.objects.get(employee_assigned_id=employee_id)
            except Employee.DoesNotExist:
                return render(request, 'skillset.html', {})
            try:
                skills = User_Skills.objects.filter(emp_mid=employee.employee_assigned_id)
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
            data = ({'lists': lists, 'designation_all': designation_all, 'department': department})
        return data


def skills(request):
    if request.method == 'GET':
        designation_all = Designation.objects.all()
        department = Department.objects.all()
        skill = request.GET.get('value')
        skill_list = Skill_Lists.objects.get(skill_name=skill)
        try:
            employee = User_Skills.objects.filter(skills_name=skill_list).values('emp_mid')
        except User_Skills.DoesNotExist:
            return render(request, 'skillset.html', {})
        lists = []
        user_details = {'name': '', 'deisgnation': '', 'department': '', 'id': '', 'doj': '', 'skills': ''}

        for val in employee:
            employee_id = val['emp_mid']
            try:
                employee = Employee.objects.get(employee_assigned_id=employee_id)
            except Employee.DoesNotExist:

                return render(request, 'skillset.html', {})
            try:
                skills = User_Skills.objects.filter(emp_mid=employee.employee_assigned_id)
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

        return render(request, 'skillset.html',
                      {'lists': lists, 'department': department, 'designation_all': designation})

def filter1(request):
    if request.method == 'GET':
        designation_all = Designation.objects.all()
        department = Department.objects.all()
        desg = request.GET.get('desg')
        depp = request.GET.get('dept')
        if depp == '-----------':
            lists_dept = designation(request)
            return render(request, 'skillset.html',
                          {'lists': lists_dept['lists'], 'department': lists_dept['department'],
                           'designation_all': lists_dept['designation_all']})
        if desg == '-----------':
            lists_dept = filters(request)

            return render(request, 'skillset.html',
                          {'lists': lists_dept['lists'], 'department': lists_dept['department'],
                           'designation_all': lists_dept['designation_all']})
        dept_name = Department.objects.filter(name=depp)
        dept_id = Department.objects.filter(id=dept_name).values('id')
        reportee_list = EmployeeCompanyInformation.objects.filter(department=dept_id).values('employee')

        lists = []
        user_details = {'name': '', 'deisgnation': '', 'department': '', 'id': '', 'doj': '', 'skills': ''}

        for val in reportee_list:
            employee_id = val['employee']

            try:
                employee = Employee.objects.get(employee_assigned_id=employee_id)
                if desg == employee.designation.name:
                    try:
                        skills = User_Skills.objects.filter(emp_mid=employee.employee_assigned_id)
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
                    if depp == dept:
                        user_details['name'] = employee.user.first_name + ' ' + employee.user.last_name
                        user_details['designation'] = employee.designation.name
                        user_details['department'] = dept
                        id = employee.idcard
                        user_details['id'] = id[:-1]
                        user_details['doj'] = employee.joined
                        user_details['skills'] = skills
                        if employee.user.is_active == True:
                            lists.append(user_details)
                            user_details = {'name': '', 'deisgnation': '', 'department': '', 'id': '', 'doj': '',
                                            'skills': ''}

            except Employee.DoesNotExist:
                return render(request, 'skillset.html', {})

        return render(request, 'skillset.html',
                      {'lists': lists, 'department': department, 'designation_all': designation})

def user(request):
    if request.method == 'GET':
        designation_all = Designation.objects.all()
        department = Department.objects.all()
        employee_id = request.GET.get('value')

        employee = Employee.objects.get(employee_assigned_id=employee_id)

        lists = []
        user_details = {'name': '', 'deisgnation': '', 'department': '', 'id': '', 'doj': '', 'skills': ''}
        try:
            skills = User_Skills.objects.filter(emp_mid=employee.employee_assigned_id)
        except User_Skills.DoesNotExist:
            skills = ''
        dept = EmployeeCompanyInformation.objects.filter(employee_id=employee.employee_assigned_id).values('department')
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

        lists.append(user_details)
        user_details = {'name': '', 'deisgnation': '', 'department': '', 'id': '', 'doj': '', 'skills': ''}

    return render(request, 'skillset.html', {'lists': lists, 'department': department, 'designation_all': designation})

def filters(request):
    designation_all = Designation.objects.all()
    department = Department.objects.all()
    dept = request.GET.get('dept')
    dept_name = Department.objects.filter(name=dept)
    dept_id = Department.objects.filter(id=dept_name).values('id')
    reportee_list = EmployeeCompanyInformation.objects.filter(department=dept_id).values('employee')
    lists = []
    user_details = {'name': '', 'deisgnation': '', 'department': '', 'id': '', 'doj': '', 'skills': ''}
    for val in reportee_list:
        employee_id = val['employee']
        employee = Employee.objects.get(employee_assigned_id=employee_id)
        try:
            skills = User_Skills.objects.filter(emp_mid=employee.employee_assigned_id)
        except User_Skills.DoesNotExist:
            skills = ''
        dept = EmployeeCompanyInformation.objects.filter(employee_id=employee.employee_assigned_id).values('department')
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
        data = ({'lists': lists, 'designation_all': designation_all, 'department': department})
    return data

def managerCheck(user):
    manager_id = Employee.objects.filter(user_id=user).values('manager_id')
    manager = Employee.objects.filter(employee_assigned_id=manager_id).values('user_id')
    if manager:
        return User.objects.get(id=manager[0]['user_id'])
