from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.views.generic import View
from django.contrib.auth.models import User
from models import MRF, Count, Position, Profile, Process
from forms import ProfileForm, MRFForm, NewMRFForm, ProcessForm
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
                context['programmingerror'] = programmingerror
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
            else:
                Count(requisition_number=requisition_number, recruiter=user, count=count).save()
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
            if position:
                MRF(requisition_number=requisition_number, position=position[0], manager=manager).save()
                mrf = MRF.objects.filter(requisition_number=requisition_number)
                Count(requisition_number=mrf[0], recruiter=user, count=count).save()
            else:
                print "not working"


        context["form"] = form
        return render(request, "newmrfform.html", context)


def designation(request):
    # import ipdb
    # ipdb.set_trace()
    response_data = {}
    department = request.GET.get('department')
    designation = Position.objects.filter(department=department).only('designation')
    designationlist = []
    if designation:
        response_data['result'] = 'Success'
        for value in designation:
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
    context_data['manager'] = mrf_detail[0].manager.first_name
    response_data['result'] = 'Success'
    response_data['details'] = json.dumps(context_data)
    response_data['message'] = serializers.serialize('json', mrf_detail)
    return HttpResponse(JsonResponse(response_data), content_type='application/json')


def candidatesearch(request):
    user = request.user.id
    countlist = Count.objects.filter(recruiter=user).values('id')
    candidatelist = Process.objects.filter(profile__requisition_number__in=countlist)
    return render(request, 'candidatemanage.html',{'candidatelist':candidatelist})


class ProcessUpdate(View):

    def get(self, request):
        context = {}
        form = ProcessForm()
        context['form'] = form
        return render(request, "processform.html", context)

    def post(self, request):
        context = {}
        form = ProcessForm(request.POST)
        context['form'] = form
        return render(request, "processform.html", context)
