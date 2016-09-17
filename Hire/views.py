from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.views.generic import View
from django.contrib.auth.models import User
from models import MRF, Count, Position, Profile, Process, RESULT_STATUS, REFERENCE_SOURCE
from forms import ProfileForm, MRFForm, NewMRFForm, ProcessForm
from datetime import date, timedelta
import json

def recruitment_form(request):
    return render(request, 'candidateform.html',{})


def mrf_view_details(request):
    requisition_no = request.GET.get('requisition_number')
    mrf_detail = MRF.objects.get(requisition_number=requisition_no)
    return render(request, '',{'mrf_detail': mrf_detail})


class Hire(View):
    def get(self, request):
        context = {"form":""}
        form = ProfileForm()
        context["form"] = form
        return render(request, "candidateform.html", context)

    def post(self, request):
        context = {"form": ""}
        form = ProfileForm(request.POST)
        if form.is_valid():
            try:
                requisition_number = Count.objects.get(requisition_number=form.cleaned_data['requisition_number'].
                                                       requisition_number.id,
                                                       recruiter=request.user.id)
                candidate_name = form.cleaned_data['candidate_name']
                mobile_number = form.cleaned_data['mobile_number']
                email_id = form.cleaned_data['email_id']
                gender = form.cleaned_data['gender']
                date_of_birth = form.cleaned_data['date_of_birth']
                source = form.cleaned_data['source']
                referred_by = form.cleaned_data['refered_by']
                interview_by = form.cleaned_data['interview_by']
                interview_on = form.cleaned_data['interview_on']
                interview_status = form.cleaned_data['interview_status']
                remark = form.cleaned_data['remark']
                mobilenocheck = uniquevalidation(mobile_number)
                if mobilenocheck:
                    context['error'] = "Candidate with same phone number is already avaliable"
                    context["form"] = form
                    return render(request, "candidateform.html", context)
                if referred_by:
                    profile = Profile(candidate_name=candidate_name, date_of_birth=date_of_birth,
                                      gender=gender, mobile_number=mobile_number, email_id=email_id,
                                      requisition_number=requisition_number, source=source,
                                      candidate_status=interview_status, referred_by=referred_by )
                else:
                    profile = Profile(candidate_name=candidate_name, date_of_birth=date_of_birth,
                                      gender=gender, mobile_number=mobile_number, email_id=email_id,
                                      requisition_number=requisition_number, source=source,
                                      candidate_status=interview_status)


                profile.save()
                process = Process.objects.create(interview_step="test", interview_status=interview_status,
                                                 interview_on=interview_on,
                        profile=profile, feedback=remark)
                process.save()
                process.interview_by.add(interview_by)
            except Exception as programmingerror:
                context['error'] = programmingerror
                context["form"] = form
                return render(request, "candidateform.html", context)

        else:
            context["form"] = form
            return render(request, "candidateform.html", context)

        return HttpResponseRedirect('/hire/candidatesearch/')





class MRFAdd(View):
    def get(self, request):
        context = {"form":""}
        form = MRFForm()
        context["form"] = form
        return render(request, "mrfform.html", context)

    def post(self, request):
        context = {"form": ""}
        form = MRFForm(request.POST)
        user = User.objects.get(id=request.user.id)
        if form.is_valid():
            requisition_number = form.cleaned_data['requisition_number']
            count = form.cleaned_data['count']
            mrfentry = Count.objects.filter(requisition_number=requisition_number, recruiter=request.user.id)
            if mrfentry:
                mrfentry = mrfentry[0]
                mrfentry.count = count
                mrfentry.save()
                context['success'] = "Requsition number updated"
            else:
                Count(requisition_number=requisition_number, recruiter=user, count=count).save()
                context['success'] = "Requsition number updated"
        context["form"] = form
        return render(request, "mrfform.html", context)


class NewMRFAdd(View):
    def get(self, request):
        context = {"form":""}
        form = NewMRFForm()
        context["form"] = form
        return render(request, "newmrfform.html", context)

    def post(self, request):
        context = {"form": ""}
        user = User.objects.get(id=request.user.id)
        form = NewMRFForm(request.POST)
        if form.is_valid():
            requisition_number = form.cleaned_data['requisition_number']
            department = form.cleaned_data['department']
            designation = form.cleaned_data['designation']
            specialization = form.cleaned_data['specialization']
            manager = form.cleaned_data['manager']
            count = form.cleaned_data['count']
            position = Position.objects.filter(department=department, designation=designation,
                                               specialization=specialization)
            requisitionnocheck = MRF.objects.filter(requisition_number=requisition_number)
            if position and not requisitionnocheck:
                MRF(requisition_number=requisition_number, position=position[0], manager=manager).save()
                mrf = MRF.objects.filter(requisition_number=requisition_number)
                Count(requisition_number=mrf[0], recruiter=user, count=count).save()
                context['success'] = "Requsition number saved"
            else:
                context['error'] = "Requsition number is already present."


        context["form"] = form
        return render(request, "newmrfform.html", context)


def designation(request):
    response_data = {}
    department = request.GET.get('department')
    designation = Position.objects.filter(department=department).only('designation')
    designationlist = []
    if designation:
        response_data['result'] = 'Success'
        for value in designation:
            if value not in designationlist:
                designationlist.append(value.designation)
    designationlist.append(".........")
    response_data['message'] = designationlist
    return HttpResponse(JsonResponse(response_data), content_type='application/json')



def specialization(request):
    response_data = {}
    designation = request.GET.get('designation')
    department = request.GET.get('department')
    specialization = Position.objects.filter(designation=designation, department=department).only('specialization')
    specializationlist = []
    if specialization:
        response_data['result'] = 'Success'
        for value in specialization:
            if value not in specializationlist:
                specializationlist.append(value.specialization)
    specializationlist.append(".........")
    response_data['message'] = specializationlist
    return HttpResponse(JsonResponse(response_data), content_type='application/json')


def mrfsearch(request):
    context_data = {}
    response_data = {}
    requisition_no = request.GET.get('requsitionno')
    mrf_detail = MRF.objects.filter(requisition_number=requisition_no)
    context_data['department'] = mrf_detail[0].position.department
    context_data['designation'] = mrf_detail[0].position.designation
    context_data['specialization'] = mrf_detail[0].position.specialization
    context_data['manager'] = mrf_detail[0].manager.first_name + " " + mrf_detail[0].manager.last_name
    response_data['result'] = 'Success'
    response_data['details'] = json.dumps(context_data)
    response_data['message'] = serializers.serialize('json', mrf_detail)
    return HttpResponse(JsonResponse(response_data), content_type='application/json')


def candidatesearch(request):
    user = request.user.id
    context_data = {'interviewdetial':[]}
    candidatelist = Profile.objects.filter(requisition_number__recruiter=user).values('id')
    for candidate in candidatelist:
        testdetail = Process.objects.filter(profile=candidate['id'])
        context_data['interviewdetial'].append(testdetail)
    context_data['REFERENCE_SOURCE'] = REFERENCE_SOURCE
    context_data['RESULT_STATUS'] = RESULT_STATUS
    return render(request, 'candidatemanage.html', context_data)


class ProcessUpdate(View):

    def get(self, request):
        context = {}
        profile = request.GET.get('profile')
        form = ProcessForm(initial={'profile_id': profile})
        context['form'] = form
        return render(request, "processform.html", context)

    def post(self, request):
        context = {}
        form = ProcessForm(request.POST)
        if form.is_valid():
            interview_by = form.cleaned_data['interview_by']
            interview_on = form.cleaned_data['interview_on']
            interview_status = form.cleaned_data['interview_status']
            remark = form.cleaned_data['remark']
            profile_id = form.cleaned_data['profile_id']
            profile = Profile.objects.get(id=profile_id)
            process = Process.objects.create(interview_step="test", interview_status=interview_status,
                                             interview_on=interview_on,
                                             profile=profile, feedback=remark)
            process.save()
            process.interview_by.add(interview_by)
            context['record_added'] = True
            context['success_msg'] = "Updated"

        context['form'] = form
        return render(request, "processform.html", context)

def uniquevalidation(mobileno):
    candidate = Profile.objects.filter(mobile_number=mobileno)
    today = date.today()
    alloweddate = today - timedelta(days=180)
    for val in candidate:
        if val.created_on > alloweddate:
            return True
    return False
