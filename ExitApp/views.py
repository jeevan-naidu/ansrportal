# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.views.generic import View
from django.contrib.auth.models import User
from .models import ResignationInfo, EmployeeClearanceInfo
from forms import UserExitForm
from tasks import ExitEmailSendTask, PostAcceptedMailMGR, PostAcceptedMailHR, LibraryClearanceMail, FinanceClearanceMail, AdminClearanceMail, MGRClearanceMail, HRClearanceMail, FacilityClearanceMail
from django.utils import timezone
from employee.models import Employee
from django.contrib import messages


# Create your views here.


def __unicode__(self):
    return unicode(self.user)


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
                mgr_id = Employee.objects.filter(user_id=userid).values('manager_id')
                manager = Employee.objects.filter(employee_assigned_id=mgr_id).values('user_id')
                manager.user.email
                context["form"] = UserExitForm()
                last_date = form.cleaned_data['last_date']
                start_date = form.cleaned_data['start_date']
                reason_dropdown = form.cleaned_data['reason_dropdown']
                comment = form.cleaned_data['comment']
                time = timezone.now()
                if start_date > last_date:
                    messages.error(request, 'You Last Date Should be Greater than resignation Date')
                    return render(request, "userexit.html", context)
                ResignationInfo(User_id=userid, last_date=last_date, emp_reason=reason_dropdown, reason_optional=comment, created_on=time, updated_on=time, hr_accepted=0, manager_accepted=0).save()
                value = Employee.objects.get(user_id=userid)
                value.resignation = start_date
                value.exit = last_date
                value.save()
                ExitEmailSendTask.delay(request.user, last_date, start_date, user_email.email)
                return render(request, "userexit.html", context)
            except Exception as programmingerror:
                print programmingerror
                messages.error(request, 'You Have already applyed for your Resignation')
                context['error'] = programmingerror
                context["form"] = UserExitForm()
                return render(request, "userexit.html", context)

        return render(request, "userexit.html", context)


class ResignationAcceptance(View):
    def get(self, request):
        context = {"form": "", "data": ""}
        allresignee = ResignationInfo.objects.all()
        id = ResignationInfo.objects.values_list('User_id')
        last_date = Employee.objects.values_list('exit').filter(user_id=id)
        context['resigneedata'] = allresignee
        context['last_date'] = last_date
        return render(request, "exitacceptance.html", context)

    def post(self, request):
        context = {"form": ""}
        form = request.POST
        allresignee = ResignationInfo.objects.all()
        context['resigneedata'] = allresignee
        hrconcent_tab ={}
        hrcomment_tab = {}
        managerconcent_tab = {}
        managercomment_tab = {}
        finaldate_tab = {}
        # import ipdb; ipdb.set_trace()
        hrconcent = {k: v for k, v in self.request.POST.items() if k.startswith('hraccepted_')}
        hrcomment = {k: v for k, v in self.request.POST.items() if k.startswith('hrcomment_')}
        managerconcent = {k: v for k, v in self.request.POST.items() if k.startswith('manageraccepted_')}
        managercomment = {k: v for k, v in self.request.POST.items() if k.startswith('managercomment_')}
        finaldate = {k: v for k, v in self.request.POST.items() if k.startswith('finaldate_')}
        for k, v in hrconcent.iteritems():
            tab_id = k.split('_')
            hrconcent_tab[tab_id[1]] = v

        for k, v in hrcomment.iteritems():
            tab_id = k.split('_')
            hrcomment_tab[tab_id[1]] = v

        for k, v in managerconcent.iteritems():
            tab_id = k.split('_')
            managerconcent_tab[tab_id[1]] = v

        for k, v in managercomment.iteritems():
            tab_id = k.split('_')
            managercomment_tab[tab_id[1]] = v

        for k, v in finaldate.iteritems():
            tab_id = k.split('_')
            finaldate_tab[tab_id[1]] = v

        try:
            for k, v in hrconcent_tab.iteritems():
                user_email = User.objects.get(id=k)
                try:
                    value = ResignationInfo.objects.get(User=k)
                    value.hr_accepted = hrconcent_tab[k]
                    value.hr_comment = hrcomment_tab[k]
                    value.save()
                    PostAcceptedMailHR.delay(user_email.first_name, user_email.email, finaldate_tab[k])
                except Exception as programmingerror:
                    context['error'] = programmingerror
                    print programmingerror
                    context['form'] = form
                    return render(request, "exitacceptance.html", context)
        except Exception as programmingerror:
                context['error'] = programmingerror
                print programmingerror
                context['form'] = form
                return render(request, "exitacceptance.html", context)
        try:
            for k, v in managerconcent_tab.iteritems():
                user_email = User.objects.get(id=k)
                try:
                    value = ResignationInfo.objects.get(User_id=k)
                    value.manager_accepted = managerconcent_tab[k]
                    value.manager_comment = managercomment_tab[k]
                    value.last_date_accepted = finaldate_tab[k]
                    value.last_date = finaldate_tab[k]
                    value.save()
                    last_date_final = Employee.objects.get(user_id=k)
                    last_date_final.exit = finaldate_tab[k]
                    last_date_final.save()
                    PostAcceptedMailMGR.delay(user_email.first_name, user_email.email, finaldate_tab[k])
                except Exception as programmingerror:
                    context['error'] = programmingerror
                    print programmingerror
                    context['form'] = form
                    return render(request, "exitacceptance.html", context)

        except Exception as programmingerror:
                context['error'] = programmingerror
                print programmingerror
                context['form'] = form
                return render(request, "exitacceptance.html", context)

        return render(request, "exitacceptance.html", context)


class ClearanceFormView(View):
    def get(self, request):
        context = {"form": "", "data": ""}
        id = request.GET.get('id')
        approved_applicant = ResignationInfo.objects.all().filter(id=id)
        clearance_data = EmployeeClearanceInfo.objects.all()
        context['approved_candidate'] = approved_applicant
        context['clearance_data'] = clearance_data
        return render(request, "departmentclearance.html", context)

    def post(self, request):
        context = {"form": ""}
        form = request.POST
        id = request.GET.get('id')
        approved_applicant = ResignationInfo.objects.all().filter(id=id)
        clearance_data = EmployeeClearanceInfo.objects.all()
        context['approved_candidate'] = approved_applicant
        context['clearance_data'] = clearance_data
        try:
            resignee_id = request.GET.get('id')
            statusby_id = request.user.id
            time = timezone.now()
            facility_amount = form['facility_amount']
            admin_amount = form['admin_amount']
            hr_amount = form['hr_amount']
            lib_amount = form['lib_amount']
            manager_amount = form['manager_amount']
            finance_amount = form['finance_amount']
            admin_feedback = form['admin_feedback']
            finance_feedback = form['finance_feedback']
            hr_feedback = form['hr_feedback']
            facility_feedback = form['facility_feedback']
            manager_feedback =  form['manager_feedback']
            library_feedback =  form['library_feedback']
            user_email = User.objects.get(id=resignee_id)

            if 'hr_approval' in form:
                hr_approval = form['hr_approval']
                try:
                    HRClearanceMail.delay(user_email.first_name, user_email.email)
                    EmployeeClearanceInfo(resignationInfo_id=resignee_id, dept_status=hr_approval,
                                          status_by_id=statusby_id,
                                          department="HR", status_on=time, dept_feedback=hr_feedback,
                                          dept_due=hr_amount).save()
                except Exception as programmingerror:
                    print programmingerror
            else:
                hr_approval = 1
            if 'facility_approval' in form:
                facility_approval = form['facility_approval']
                try:
                    FacilityClearanceMail.delay(user_email.first_name, user_email.email)
                    EmployeeClearanceInfo(resignationInfo_id=resignee_id, dept_status=facility_approval,
                                          status_by_id=statusby_id,
                                          department="FAC", status_on=time, dept_feedback=facility_feedback,
                                          dept_due=facility_amount).save()
                except Exception as programmingerror:
                    print programmingerror
            else:
                facility_approval = 1
            if 'finance_approval' in form:
                finance_approval = form['finance_approval']
                try:
                    FinanceClearanceMail.delay(user_email.first_name, user_email.email)
                    EmployeeClearanceInfo(resignationInfo_id=resignee_id, dept_status=finance_approval,
                                          status_by_id=statusby_id,
                                          department="FIN", status_on=time, dept_feedback=finance_feedback,
                                          dept_due=finance_amount).save()
                except Exception as programmingerror:
                    print programmingerror
            else:
                finance_approval =1
            if 'manager_approval' in form:
                manager_approval = form['manager_approval']
                try:
                    MGRClearanceMail.delay(user_email.first_name, user_email.email)
                    EmployeeClearanceInfo(resignationInfo_id=resignee_id, dept_status=manager_approval,
                                          status_by_id=statusby_id,
                                          department="MGR", status_on=time, dept_feedback=manager_feedback,
                                          dept_due=manager_amount).save()
                except Exception as programmingerror:
                    print programmingerror
            else:
                manager_approval = 1
            if 'admin_approval' in form:
                admin_approval = form['admin_approval']
                try:
                    AdminClearanceMail.delay(user_email.first_name, user_email.email)
                    EmployeeClearanceInfo(resignationInfo_id=resignee_id, dept_status=admin_approval,
                                          status_by_id=statusby_id,
                                          department="IT", status_on=time, dept_feedback=admin_feedback,
                                          dept_due=admin_amount).save()
                except Exception as programmingerror:
                    print programmingerror
            else:
                admin_approval =1
            if 'library_approval' in form:
                library_approval = form['library_approval']
                try:
                    LibraryClearanceMail.delay(user_email.first_name, user_email.email)
                    EmployeeClearanceInfo(resignationInfo_id=resignee_id, dept_status=library_approval, status_by_id=statusby_id,
                                          department="LIB", status_on=time, dept_feedback=library_feedback,
                                          dept_due=lib_amount).save()
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
        approved_applicant = ResignationInfo.objects.all()
        context['approved_candidate'] = approved_applicant
        return render(request, "clearancelist.html", context)









