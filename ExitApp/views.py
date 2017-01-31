# -*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse
from django.views.generic import View
from .models import ResignationInfo, EmployeeClearanceInfo
from forms import UserExitForm
from tasks import ExitEmailSendTask, PostAcceptedMailMGR, PostAcceptedMailHR, \
    LibraryClearanceMail, FinanceClearanceMail, AdminClearanceMail, MGRClearanceMail, \
    HRClearanceMail, FacilityClearanceMail, AdayBeforeEmail
from django.utils import timezone
from employee.models import Employee
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import timedelta
from datetime import date
from django.core.exceptions import PermissionDenied
from django.db.models import Q


# Create your views here.


def __unicode__(self):
    return unicode(self.user)


def revert_resignation(request):
    user_id = request.user.id
    note = request.GET['message']
    try:
        value = Employee.objects.get(user_id=user_id)
        value.resignation = '1111-11-11'
        value.exit = '1111-11-11'
        value.save()
        exit_revert = ResignationInfo.objects.get(User_id=user_id)
        exit_revert.exit_revert_flag = 1
        exit_revert.manager_accepted = 0
        exit_revert.hr_accepted = 0
        exit_revert.exit_revert_note = note
        exit_revert.save()
    except Exception as programmingerror:
        print programmingerror
        return HttpResponse(programmingerror)

    return HttpResponse('success')


def exit_note_update(request):
    value = request.GET['id']
    exit_summary = request.GET['message']
    exit_flag = request.GET['exit_flag']
    exit_id = ResignationInfo.objects.get(id=value)
    value = User.objects.get(id=exit_id.User_id)
    value.is_staff = 0
    value.is_active = 0
    value.is_superuser = 0
    value.save()
    exit_id.exit_interview_notes = exit_summary
    exit_id.exit_interview_flag = exit_flag
    exit_id.save()
    return HttpResponse('success')


def update_manager_concent(request):
    id = request.GET['id']
    mgr_id = Employee.objects.get(user_id=id)
    manager = Employee.objects.get(employee_assigned_id=mgr_id.manager_id)
    manageremail = User.objects.get(id=manager.user_id)
    user_email = User.objects.get(id=id)
    final_date = request.GET['final_date']
    mgr_backup = request.GET['mgr_backup']
    mgr_feedback = request.GET['mgr_feedback']
    manager_concent = request.GET['manager_concent']
    rehire_manager = request.GET['manager_rehire']
    resign_info = ResignationInfo.objects.get(User_id=id)
    resign_info.rehire_manager = rehire_manager
    resign_info.manager_comment = mgr_feedback
    resign_info.last_date_accepted = final_date
    resign_info.manager_accepted = manager_concent
    resign_info.backup_taken = mgr_backup
    resign_info.last_date = final_date
    resign_info.updated_on = timezone.now()
    resign_info.save()
    PostAcceptedMailMGR.delay(user_email.first_name, user_email.email, final_date, manageremail.email)
    return HttpResponse('success')


def update_hr_concent(request):
    id = request.GET['id']
    user_email = User.objects.get(id=id)
    final_date = request.GET['final_date']
    hr_feedback = request.GET['hr_feedback']
    hr_concent = request.GET['hr_concent']
    hr_rehire = request.GET['hr_rehire']
    resign_info = ResignationInfo.objects.get(User_id=id)
    resign_info.rehire_hr = hr_rehire
    resign_info.hr_comment = hr_feedback
    resign_info.last_date_accepted = final_date
    resign_info.hr_accepted = hr_concent
    resign_info.last_date = final_date
    resign_info.updated_on = timezone.now()
    resign_info.save()
    PostAcceptedMailHR.delay(user_email.first_name, user_email.email, final_date)
    return HttpResponse('success')




class ExitFormAdd(View):
    def get(self, request):
        context = {"form": ""}
        form = UserExitForm()
        context["form"] = form
        return render(request, "userexit.html", context)

    def post(self, request):
        context = {"form": ""}
        form = UserExitForm(request.POST)
        if form.is_valid():
            try:
                userid = request.user.id
                user_email = User.objects.get(id=userid)
                mgr_id = Employee.objects.get(user_id=request.user.id)
                manager = Employee.objects.get(employee_assigned_id=mgr_id.manager_id)
                manageremail = User.objects.get(id=manager.user_id)
                today_date = date.today()
                context["form"] = UserExitForm()
                last_date = form.cleaned_data['last_date']
                start_date = form.cleaned_data['start_date']
                reason_dropdown = form.cleaned_data['reason_dropdown']
                comment = form.cleaned_data['comment']
                time = timezone.now()
                if start_date > last_date:
                    messages.error(request, 'Your Last Date Should be Greater than resignation Date')
                    return render(request, "userexit.html", context)
                if start_date < today_date:
                    messages.error(request, 'Please select Resignation Date today or after')
                    return render(request, "userexit.html", context)
                ResignationInfo(User_id=userid, last_date=last_date, emp_reason=reason_dropdown,
                                reason_optional=comment, created_on=time, updated_on=time, hr_accepted=0,
                                manager_accepted=0, exit_revert_flag=0).save()
                value = Employee.objects.get(user_id=userid)
                value.resignation = start_date
                value.exit = last_date
                value.save()
                ExitEmailSendTask.delay(request.user, last_date, start_date, user_email.email, manageremail.email)
                messages.success(request, 'Thanks ! Your Resignation has been Submitted')
                return render(request, "userexit.html", context)
            except Exception as programmingerror:
                print programmingerror
                messages.error(request, 'You Have already applyed for your Resignation')
                context['error'] = programmingerror
                context["form"] = UserExitForm()
                return render(request, "userexit.html", context)
        form = UserExitForm()
        context["form"] = form
        return render(request, "userexit.html", context)


class ResignationAcceptance(View):
    def get(self, request):
        context = {"form": "", "data": ""}
        mgrid = Employee.objects.get(user_id=request.user.id)
        reportee = Employee.objects.filter(manager_id=mgrid)
        filterdata = []
        for value in reportee:
            filterdata.append(value.user.id)
        allresignee = ResignationInfo.objects.filter(User__in=filterdata).exclude(User_id=request.user.id)
        context['resigneedata'] = allresignee
        return render(request, "exitacceptance.html", context)


class ResignationAcceptanceHR(View):
    def get(self, request):
        context = {"form": "", "data": ""}
        allresignee = ResignationInfo.objects.filter(~Q(User_id=request.user.id))
        context['resigneedata'] = allresignee
        return render(request, "hracceptance.html", context)


class ClearanceFormView(View):
    def get(self, request):
        context = {"form": "", "data": ""}
        id = request.GET.get('id')
        if request.user.groups.filter(name__in=['myansrsourceHR', 'BookingRoomAdmin', 'Finance', 'IT-support',
                                                'LibraryAdmin',]).exists():
            clearance_data = EmployeeClearanceInfo.objects.filter(resignationInfo=id)
            candidate_detail = ResignationInfo.objects.filter(id=id)
            context['dataresignee'] = clearance_data
            if not candidate_detail:
                raise PermissionDenied("Sorry You Don't Have any record")
            context['candidate_detail'] = candidate_detail
        else:
            mgrid = Employee.objects.get(user_id=request.user.id)
            reportee = Employee.objects.filter(manager_id=mgrid)
            filterdata = []
            for value in reportee:
                filterdata.append(value.user.id)
            allresignee = ResignationInfo.objects.filter(User__in=filterdata)
            if not allresignee:
                raise PermissionDenied("Sorry You Don't Have any record")
            clearance_data = EmployeeClearanceInfo.objects.all().filter(resignationInfo=id)
            candidate_detail = ResignationInfo.objects.filter(id=id)
            context['candidate_detail'] = candidate_detail
            if not candidate_detail:
                raise PermissionDenied("Sorry You Don't Have any record")
            context['dataresignee'] = clearance_data
        return render(request, "departmentclearance.html", context)

    def post(self, request):
        context = {"form": ""}
        form = request.POST
        id = request.GET.get('id')
        if request.user.groups.filter(name__in=['myansrsourceHR', 'BookingRoomAdmin', 'Finance', 'IT-support',
                                                'LibraryAdmin']).exists():
            allresignee = ResignationInfo.objects.all()
            context['resigneedata'] = allresignee
            candidate_detail = ResignationInfo.objects.filter(id=id)
            context['candidate_detail'] = candidate_detail
            clearance_data = EmployeeClearanceInfo.objects.filter(resignationInfo=id)
            context['dataresignee'] = clearance_data
        else:
            mgrid = Employee.objects.get(user_id=request.user.id)
            reportee = Employee.objects.filter(manager_id=mgrid)
            filterdata = []
            for value in reportee:
                filterdata.append(value.user.id)
            allresignee = ResignationInfo.objects.filter(User__in=filterdata)
            if not allresignee:
                raise PermissionDenied("Sorry You Don't Have any record")
            context['resigneedata'] = allresignee
            candidate_detail = ResignationInfo.objects.filter(id=id)
            context['candidate_detail'] = candidate_detail
            clearance_data = EmployeeClearanceInfo.objects.filter(resignationInfo=id)
            context['dataresignee'] = clearance_data
        try:
            resignee_id = request.GET.get('id')
            statusby_id = request.user.id
            time = timezone.now()
            user_detail = ResignationInfo.objects.get(id=resignee_id)
            user_email = User.objects.get(id=user_detail.User_id)
            form = request.POST
            count = EmployeeClearanceInfo.objects.filter(resignationInfo_id=resignee_id).count()

            if 'hr_approval' in form:
                if count == 5:
                    hr_approval = form['hr_approval']
                    hr_amount = form['hr_amount']
                    hr_feedback = form['hr_feedback']
                    mgr_id = Employee.objects.get(user_id=request.user.id)
                    try:
                        EmployeeClearanceInfo(resignationInfo_id=resignee_id, dept_status=hr_approval,
                                              status_by_id=statusby_id,
                                              department="HR", status_on=time, dept_feedback=hr_feedback,
                                              dept_due=hr_amount).save()
                        HRClearanceMail.delay(user_email.first_name, user_email.email)
                        messages.success(request, 'Your response has been submitted successfully')
                        messages.info(request, 'Done')
                    except Exception as programmingerror:
                        print programmingerror
                elif count == 6:
                    messages.success(request, 'Nothing to Update')
                else:
                    messages.error(request, 'Hr is not suppose to update unless all department have checked')
            else:
                hr_approval = 1

            if 'facility_approval' in form:
                facility_approval = form['facility_approval']
                facility_amount = form['facility_amount']
                facility_feedback = form['facility_feedback']
                try:
                    EmployeeClearanceInfo(resignationInfo_id=resignee_id, dept_status=facility_approval,
                                          status_by_id=statusby_id,
                                          department="FAC", status_on=time, dept_feedback=facility_feedback,
                                          dept_due=facility_amount).save()
                    FacilityClearanceMail.delay(user_email.first_name, user_email.email)
                    messages.success(request, 'Your response has been submitted successfully')
                except Exception as programmingerror:
                    print programmingerror
            else:
                facility_approval = 1
            if 'finance_approval' in form:
                finance_approval = form['finance_approval']
                finance_amount = form['finance_amount']
                finance_feedback = form['finance_feedback']
                try:
                    EmployeeClearanceInfo(resignationInfo_id=resignee_id, dept_status=finance_approval,
                                          status_by_id=statusby_id,
                                          department="FIN", status_on=time, dept_feedback=finance_feedback,
                                          dept_due=finance_amount).save()
                    FinanceClearanceMail.delay(user_email.first_name, user_email.email)
                    messages.success(request, 'Your response has been submitted successfully')
                except Exception as programmingerror:
                    print programmingerror
            else:
                finance_approval =1
            if 'manager_approval' in form:
                urlid = request.GET.get('id')
                user_id = ResignationInfo.objects.values('User_id').filter(id=urlid)
                mgr_id = Employee.objects.get(user_id=user_id)
                manager = Employee.objects.get(employee_assigned_id=mgr_id.manager_id)
                manager_email = User.objects.get(id=manager.user_id)
                manager_approval = form['manager_approval']
                manager_amount = form['manager_amount']
                manager_feedback = form['manager_feedback']
                try:
                    EmployeeClearanceInfo(resignationInfo_id=resignee_id, dept_status=manager_approval,
                                          status_by_id=statusby_id,
                                          department="MGR", status_on=time, dept_feedback=manager_feedback,
                                          dept_due=manager_amount).save()
                    MGRClearanceMail.delay(user_email.first_name, user_email.email, manager_email.email)
                    messages.success(request, 'Your response has been submitted successfully')
                except Exception as programmingerror:
                    print programmingerror
            else:
                manager_approval = 1
            if 'admin_approval' in form:
                admin_amount = form['admin_amount']
                admin_approval = form['admin_approval']
                admin_feedback = form['admin_feedback']
                try:
                    EmployeeClearanceInfo(resignationInfo_id=resignee_id, dept_status=admin_approval,
                                          status_by_id=statusby_id,
                                          department="IT", status_on=time, dept_feedback=admin_feedback,
                                          dept_due=admin_amount).save()
                    AdminClearanceMail.delay(user_email.first_name, user_email.email)
                    messages.success(request, 'Your response has been submitted successfully')
                except Exception as programmingerror:
                    print programmingerror
            else:
                admin_approval =1
            if 'library_approval' in form:
                library_approval = form['library_approval']
                lib_amount = form['lib_amount']
                library_feedback = form['library_feedback']
                try:
                    EmployeeClearanceInfo(resignationInfo_id=resignee_id, dept_status=library_approval, status_by_id=statusby_id,
                                          department="LIB", status_on=time, dept_feedback=library_feedback,
                                          dept_due=lib_amount).save()
                    LibraryClearanceMail.delay(user_email.first_name, user_email.email)
                    messages.success(request, 'Your response has been submitted successfully')
                except Exception as programmingerror:
                    print programmingerror
            else:
                library_approval = 1
        except Exception as programmingerror:
            context['error'] = programmingerror
            print programmingerror
            context['form'] = form
            return render(request, "departmentclearance.html", context)

        return render(request, "departmentclearance.html", context)


class ClearanceList(View):
    def get(self, request):
        context = {"form": "", "data": ""}
        if request.user.groups.filter(name__in=['myansrsourceHR', 'BookingRoomAdmin', 'Finance', 'IT-support',
                                                'LibraryAdmin']).exists():
            d = date.today()
            final_val = d + timedelta(days=1)
            allresignee = ResignationInfo.objects.filter(last_date_accepted__lte=final_val).exclude(
                User_id=request.user.id)
            print allresignee
            context['approved_candidate'] = allresignee
        else:
            mgrid = Employee.objects.get(user_id=request.user.id)
            reportee = Employee.objects.filter(manager_id=mgrid)
            filterdata = []
            d = date.today()
            final_val = d + timedelta(days=1)
            for value in reportee:
                filterdata.append(value.user.id)
            allresignee = ResignationInfo.objects.filter(User__in=filterdata, last_date_accepted__lte=final_val).exclude(
                User_id=request.user.id)
            email_candidate = ResignationInfo.objects.filter(User__in=filterdata, last_date_accepted=final_val).exclude(
                User_id=request.user.id)
            for data in email_candidate:
                candidate_first_name = User.objects.values('first_name', 'email').filter(id=data.User_id)
                for key in candidate_first_name:
                    AdayBeforeEmail.delay(key['first_name'], key['email'])
            context['approved_candidate'] = allresignee
        return render(request, "clearancelist.html", context)








