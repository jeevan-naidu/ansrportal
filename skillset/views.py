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

def SkillSet(request):
    if request.method == 'GET':
        user = request.user
        if request.user.groups.filter(name__in=['myansrsourceHR']).exists() or request.user.is_superuser == True:
            designation_all = []
            department = []
            skills_all = []
            reportee = Employee.objects.select_related('designation', 'user').filter(user__is_active=True)
            lists = []
            user_details = {"name": "", "deisgnation": "", "department": "", "id": "", "doj": "", "skills": ""}
            for employee in reportee:
                designation_all.append(employee.designation.name)
                designation_all = sorted(set(designation_all))
                try:
                    skillset = User_Skills.objects.filter(emp_mid=employee.employee_assigned_id).values('skills_name','skills_type')
                    skills_list = []
                    skills_dict = {'skills_name':'','skills_type':''}
                    for skill in skillset:
                        skills_dict['skills_name'] = skill['skills_name']
                        skills_dict['skills_type'] = skill['skills_type']
                        skills_list.append(skills_dict)
                        skills_dict = {'skills_name':'','skills_type':''}
                    if skills_list:
                        for skills_user in skills_list:
                            skills_all.append(skills_user['skills_name'])
                    skills_all = sorted(set(skills_all))
                except User_Skills.DoesNotExist:
                    skills_list = None
                try:
                    depart = EmployeeCompanyInformation.objects.get(employee_id=employee.employee_assigned_id)
                    dept = depart.department.name
                except:
                    dept = ""
                department.append(dept)
                department = sorted(set(department))
                user_details['name'] = employee.user.first_name + ' ' + employee.user.last_name
                user_details['designation'] = employee.designation.name
                user_details['department'] = dept
                id = employee.idcard
                user_details['id'] = id[:-1]
                user_details['doj'] = employee.joined
                user_details['skills'] = skills_list
                lists.append(user_details)
                user_details = {"name": "", "deisgnation": "", "department": "", "id": "", "doj": "",  "skills": ""}

        elif request.user.groups.filter(name__in=['myansrsourcePM']).exists():
            employee = Employee.objects.get(user_id=user.id)
            designation_all = []
            department = []
            skills_all = []
            mgrid = Employee.objects.get(user_id=request.user.id)
            reportee_business_unit = BusinessUnit.objects.filter(new_bu_head=mgrid.user_id)
            if not reportee_business_unit:
                reportee = Employee.objects.filter(manager_id=mgrid, user__is_active=True)
                lists = []
                user_details = {"name": "", "deisgnation": "", "department": "", "id": "", "doj": "", "skills": ""}
                for employee in reportee:
                    designation_all.append(employee.designation.name)
                    designation_all = sorted(set(designation_all))
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
                        if skills_list:
                            for skills_user in skills_list:
                                skills_all.append(skills_user['skills_name'])
                        skills_all = sorted(set(skills_all))
                    except User_Skills.DoesNotExist:
                        skills_list = None
                    try:
                        depart = EmployeeCompanyInformation.objects.get(employee_id=employee.employee_assigned_id)
                        dept = depart.department.name
                    except:
                        dept = ""
                    department.append(dept)
                    department = sorted(set(department))
                    user_details['name'] = employee.user.first_name + ' ' + employee.user.last_name
                    user_details['designation'] = employee.designation.name
                    user_details['department'] = dept
                    id = employee.idcard
                    user_details['id'] = id[:-1]
                    user_details['doj'] = employee.joined
                    user_details['skills'] = skills_list
                    lists.append(user_details)
                    user_details = {"name": "", "deisgnation": "", "department": "", "id": "", "doj": "",
                                        "skills": ""}

            else:
                reportee = Employee.objects.filter(business_unit=reportee_business_unit, user__is_active=True)
                lists = []
                user_details = {"name": "", "deisgnation": "", "department": "", "id": "", "doj":"" , "skills": ""}
                for employee in reportee:
                    try:
                        skillset = User_Skills.objects.filter(emp_mid=employee.employee_assigned_id).values('skills_name','skills_type')
                        skills_list = []
                        skills_dict = {'skills_name':'','skills_type':''}
                        for skill in skillset:
                            skills_dict['skills_name'] = skill['skills_name']
                            skills_dict['skills_type'] = skill['skills_type']
                            skills_list.append(skills_dict)
                            skills_dict = {'skills_name':'','skills_type':''}
                        if skills_list:
                            for skills_user in skills_list:
                                skills_all.append(skills_user['skills_name'])
                        skills_all = sorted(set(skills_all))
                    except User_Skills.DoesNotExist:
                        skills_list = None
                    try:
                        depart = EmployeeCompanyInformation.objects.get(employee_id=employee.employee_assigned_id)
                        dept = depart.department.name
                    except:
                        dept = ""
                    department.append(dept)
                    department = sorted(set(department))
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
                              {'lists': lists, 'json_list': json_list, 'count': count,
                               'skills_all': skills_all, 'designation_all': designation_all, 'department': department})

        else:
            employee = Employee.objects.get(user_id=user.id)

            lists = []
            user_details = {"name": "", "deisgnation": "", "department": "", "id": "", "doj": "", "skills": ""}
            try:
                skills = User_Skills.objects.filter(emp_mid=employee.employee_assigned_id)
            except User_Skills.DoesNotExist:
                skills = ''
            try:
                depart = EmployeeCompanyInformation.objects.get(employee_id=employee.employee_assigned_id)
                dept = depart.department.name
            except:
                dept = ""
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
                          {'lists': lists})

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

        return render(request, 'skillset.html', {'lists':lists, 'json_list':json_list, 'count':count, 'skills_all': skills_all,
                                                 'designation_all': designation_all, 'department': department})

def managerCheck(user):
    manager_id = Employee.objects.filter(user_id=user).values('manager_id')
    manager = Employee.objects.filter(employee_assigned_id=manager_id).values('user_id')
    if manager:
        return User.objects.get(id=manager[0]['user_id'])
