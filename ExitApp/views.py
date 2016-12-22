# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.models import User
from .models import ResignationInfo, EmployeeFeedback, ClearanceInfo
from forms import UserExitForm, ResignationAcceptanceForm, ClearanceForm
from tasks import ExitEmailSendTask, PostAcceptedMail, LibraryClearanceMail, ITClearanceMail, AdminClearanceMail
from django.utils import timezone


# Create your views here.

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
                import ipdb;ipdb.set_trace()
                last_date = request.session['lastdate'] = form.cleaned_data['last_date']
                ExitEmailSendTask.delay(request.user, last_date, )
                reason_dropdown = form.cleaned_data['reason_dropdown']
                comment = form.cleaned_data['comment']
                time = timezone.now()
                user_id = request.user.id
                form_value = ResignationInfo(User_id=user_id, last_date=last_date, emp_reason=reason_dropdown, reason_optional=comment, created_on=time, updated_on=time, hr_accepted=0, manager_accepted=0)
                form_value.save()
            except Exception as programmingerror:
                context['error'] = programmingerror
                print context['error']
                context["form"] = form
                return render(request, "userexit.html", context)

        return render(request, "userexit.html", context)


class ResignationAcceptance(View):
    def get(self, request):
        context = {"form": ""}
        form = ResignationAcceptanceForm()
        context['form'] = form
        return render(request, "exitacceptance.html", context)

    def post(self, request):
        context = {"form": ""}
        form = ResignationAcceptanceForm(request.POST)
        if form.is_valid():
            try:
                user_id = form.cleaned_data['exit_applicant']
                hr_feedback = form.cleaned_data['hr_feedback']
                manager_feedback = form.cleaned_data['manager_feedback']
                manger_concent = form.cleaned_data['manager_accepted']
                hr_concent = form.cleaned_data['hr_accepted']
                # laste_date_accepted = form.cleaned_data['last_date_accepted']
                user_email = User.objects.get(id=user_id.id)
                PostAcceptedMail.delay(user_id, user_email.email, laste_date_accepted)
                value = ResignationInfo.objects.get(User=user_id)
                value.hr_accepted = hr_concent
                value.manager_accepted = manger_concent
                # value.last_date_accepted = laste_date_accepted
                value.save()
                EmployeeFeedback(employee_id_id=value.id, manager_feedback=manager_feedback, hr_feedback=hr_feedback,).save()
                # import ipdb;ipdb.set_trace()
                ClearanceInfo(hr_clearance=hr_concent, IT_clearance=0, admin_clearance=0, library_clearance=0, manager_clearance=manger_concent, resign_id=value.id).save()
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
                librarian_accepted = form.cleaned_data['librarian_accepted']
                librarian_feedback = form.cleaned_data['librarian_feedback']
                admin_accepted = form.cleaned_data['admin_accepted']
                admin_feedback = form.cleaned_data['admin_feedback']
                it_accepted = form.cleaned_data['it_accepted']
                it_feedback = form.cleaned_data['it_feedback']
                user_detail = User.objects.get(id=user_id.id)
                if librarian_accepted is not None:
                    LibraryClearanceMail.delay(user_id, user_detail.email)
                if admin_accepted is not None:
                    AdminClearanceMail.delay(user_id, user_detail.email)
                if it_accepted is not None:
                    ITClearanceMail.delay(user_id, user_detail.email)

                clearancevalue = ClearanceInfo.objects.get(resign=user_id)
                clearancevalue.IT_clearance = it_accepted
                clearancevalue.admin_clearance = admin_accepted
                clearancevalue.library_clearance = librarian_accepted
                clearancevalue.save()
                value = EmployeeFeedback.objects.get(employee_id=user_id)
                value.it_feedback = it_feedback
                value.library_feedback = librarian_feedback
                value.admin_feedback = admin_feedback
                value.save()
            except Exception as programmingerror:
                context['error'] = programmingerror
                print programmingerror
                context['form'] = form
                return render(request, "departmentclearance.html", context)

        return render(request, "departmentclearance.html", context)









