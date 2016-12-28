# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.views.generic import View
from django.contrib.auth.models import User
from .models import ResignationInfo
from forms import UserExitForm, ResignationAcceptanceForm, ClearanceForm
from tasks import ExitEmailSendTask, PostAcceptedMail, LibraryClearanceMail, ITClearanceMail, AdminClearanceMail
from django.utils import timezone
from employee.models import Employee


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
                last_date = form.cleaned_data['last_date']
                start_date = form.cleaned_data['start_date']
                ExitEmailSendTask.delay(request.user, last_date, start_date )
                reason_dropdown = form.cleaned_data['reason_dropdown']
                comment = form.cleaned_data['comment']
                time = timezone.now()
                userid = request.user.id
                ResignationInfo(User_id=userid, last_date=last_date, emp_reason=reason_dropdown, reason_optional=comment, created_on=time, updated_on=time, hr_accepted=0, manager_accepted=0).save()
                value = Employee.objects.get(user_id=userid)
                value.resignation = start_date
                value.save()
            except Exception as programmingerror:
                context['error'] = programmingerror
                print context['error']
                context["form"] = form
                return render(request, "userexit.html", context)

        return render(request, "userexit.html", context)


class ResignationAcceptance(View):
    def get(self, request):
        context = {"form": "", "data": ""}
        form = ResignationAcceptanceForm()
        allresignee = ResignationInfo.objects.all()
        context['form'] = form
        # context['id'] = request.user.id
        context['resigneedata'] = allresignee
        return render(request, "exitacceptance.html", context)

    def post(self, request):
        context = {"form": ""}
        form = request.POST
        hrconcent_tab ={}
        hrcomment_tab = {}
        managerconcent_tab = {}
        managercomment_tab = {}
        finaldate_tab = {}
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
                PostAcceptedMail.delay(user_email.first_name, user_email.email, finaldate_tab[k])
                value = ResignationInfo.objects.get(User=k)
                value.hr_accepted = hrconcent_tab[k]
                value.manager_accepted = managerconcent_tab[k]
                value.manager_comment = managercomment_tab[k]
                value.hr_comment = hrcomment_tab[k]
                value.last_date_accepted = '2016-12-18 18:30:00.000000'
                value.save()
        except Exception as programmingerror:
                context['error'] = programmingerror
                print programmingerror
                context['form'] = form
                return render(request, "exitacceptance.html", context)

        return render(request, "exitacceptance.html", context)


class ClearanceFormView(View):
    def get(self, request):
        context = {"form": ""}
        form = ClearanceForm()
        context['form'] = form
        return render(request, "departmentclearance.html", context)

    def post(self, request):
        # import ipdb;ipdb.set_trace()
        context = {"form": ""}
        form = ClearanceForm(request.POST)
        if form.is_valid():
            try:
                user_id = form.cleaned_data['exit_applicant_list']
                # librarian_accepted = form.cleaned_data['librarian_accepted']
                # librarian_feedback = form.cleaned_data['librarian_feedback']
                # admin_accepted = form.cleaned_data['admin_accepted']
                # admin_feedback = form.cleaned_data['admin_feedback']
                # it_accepted = form.cleaned_data['it_accepted']
                # it_feedback = form.cleaned_data['it_feedback']
                # user_detail = User.objects.get(id=user_id.id)
                # if librarian_accepted is not None:
                #     LibraryClearanceMail.delay(user_id, user_detail.email)
                # if admin_accepted is not None:
                #     AdminClearanceMail.delay(user_id, user_detail.email)
                # if it_accepted is not None:
                #     ITClearanceMail.delay(user_id, user_detail.email)
                #
                # clearancevalue = ClearanceInfo.objects.get(resign=user_id)
                # clearancevalue.IT_clearance = it_accepted
                # clearancevalue.admin_clearance = admin_accepted
                # clearancevalue.library_clearance = librarian_accepted
                # clearancevalue.save()
                # value = EmployeeFeedback.objects.get(employee_id=user_id)
                # value.it_feedback = it_feedback
                # value.library_feedback = librarian_feedback
                # value.admin_feedback = admin_feedback
                # value.save()
            except Exception as programmingerror:
                context['error'] = programmingerror
                print programmingerror
                context['form'] = form
                return render(request, "departmentclearance.html", context)

        return render(request, "departmentclearance.html", context)









