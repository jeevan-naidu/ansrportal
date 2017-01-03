from django.shortcuts import render, redirect, render_to_response
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.views.generic import View
from django.contrib import messages
from django.views.generic import CreateView
from formtools.wizard.views import SessionWizardView
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from models import Address, UserDetails, Education, PreviousEmployment, Proof
from forms import UserDetailsForm, EducationForm, PreviousEmploymentForm, ProofForm, UserRegistrationForm

AllowedFileTypes = ['jpg', 'csv','png', 'pdf', 'xlsx', 'xls', 'docx', 'doc', 'jpeg', 'eml']
# Create your views here.
def EmployeeWelcome(request):
    return render(request, 'welcome.html',{})

def login(request):
	context = {}
	context.update(csrf(request))
	return render_to_response('login.html',context)

def auth_view(request):
	username = request.POST.get('username','')
	password = request.POST.get('password','')
	user = auth.authenticate(username=username, password=password)

	if user is not None:
		auth.login(request, user)
		return HttpResponseRedirect('/myansrsource/loggedin')
	else:
		return HttpResponseRedirect('/myansrsource/invalid')

# def password_change(request):
#     if request.method == 'POST':
# 		form = PasswordChangeForm(request.POST)
# 		if form.is_valid():
# 			form.save()
# 			return HttpResponseRedirect('/myansrsource/password_change')
#
#     context = {}
#     context.update(csrf(request))
#
#     context['form'] = PasswordChangeForm()
#     return render_to_response(request, 'password_change.html', context)

def logout(request):
	auth.logout(request)
	return render_to_response('logout.html')

def loggedin(request):
	return render_to_response('loggedin.html',{'user':request.user.username})

def invalid_login(request):
	return render_to_response('invalid.html')

def register(request):
    # import ipdb; ipdb.set_trace()
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/myansrsource/register_success')
        else:
            print form.errors
    context = {}
    context.update(csrf(request))

    context['form'] = UserRegistrationForm()

    return render_to_response('register.html', context)

def register_success(request):
	return HttpResponseRedirect("/myansrsource/login")

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
@login_required
def user_details(request):

    # user details form
    if request.method == 'GET':
        context = {"form":""}
        form = UserDetailsForm()
        context["form"] = form
        #import ipdb; ipdb.set_trace()
        user = request.user
        try:
            employee = UserDetails.objects.get(employee=request.user)
        except UserDetails.DoesNotExist:
            context = {"form":""}
            form = UserDetailsForm()
            context["form"] = form
            return render(request, "wizard.html", context)
        first_name = user.first_name
        last_name = user.last_name
        middle_name = employee.middle_name
        nationality = employee.nationality
        marital_status = employee.marital_status
        wedding_date = employee.wedding_date
        date_of_birth = employee.date_of_birth
        blood_group = employee.blood_group
        land_phone = employee.land_phone
        emergency_phone1 = employee.emergency_phone1
        emergency_phone2 = employee.emergency_phone2
        mobile_phone = employee.mobile_phone
        personal_email = employee.personal_email
        gender = employee.gender
        form = UserDetailsForm(initial = {'first_name':request.user.first_name,'last_name':request.user.last_name,'middle_name':employee.middle_name,
        'nationality':employee.nationality,'marital_status':employee.marital_status,'wedding_date':wedding_date,'date_of_birth':date_of_birth,'blood_group':employee.blood_group,
        'land_phone':employee.land_phone,'emergency_phone1':employee.emergency_phone1,'emergency_phone2':employee.emergency_phone2,'mobile_phone':employee.mobile_phone,
        'personal_email':employee.personal_email,'gender':employee.gender})

        context["form"] = form
        return render(request, "wizard.html", context)

    if request.method == 'POST':
        #import ipdb; ipdb.set_trace()
        context = {"form":""}
        form = UserDetailsForm(request.POST)

        if form.is_valid():
            employee = User.objects.get(username=request.user)
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            middle_name = form.cleaned_data['middle_name']
            nationality = form.cleaned_data['nationality']
            marital_status = form.cleaned_data['marital_status']
            wedding_date = form.cleaned_data['wedding_date']
            date_of_birth = form.cleaned_data['date_of_birth']
            blood_group = form.cleaned_data['blood_group']
            land_phone = form.cleaned_data['land_phone']
            emergency_phone1 = form.cleaned_data['emergency_phone1']
            emergency_phone2 = form.cleaned_data['emergency_phone2']
            mobile_phone = form.cleaned_data['mobile_phone']
            personal_email = form.cleaned_data['personal_email']
            gender = form.cleaned_data['gender']

            UserDetails(employee = employee,
            middle_name=middle_name,
            nationality=nationality,
            marital_status=marital_status,
            wedding_date=wedding_date,
            date_of_birth=date_of_birth,
            blood_group=blood_group,
            land_phone=land_phone,
            emergency_phone1=emergency_phone1,
            emergency_phone2=emergency_phone2,
            mobile_phone=mobile_phone,
            personal_email=personal_email,
            gender=gender).save()
            context['form'] = form
            return HttpResponseRedirect("/myansrsource/user_details/education")

@csrf_exempt
@login_required
def education(request):
    #education form
    # import ipdb; ipdb.set_trace()
    if request.method == 'GET':
        context_data = {"education_form":""}
        education_form = EducationForm()
        context_data["education_form"] = education_form
        #import ipdb; ipdb.set_trace()
        user = request.user
        try:
            employee = Education.objects.get(employee=request.user)
        except Education.DoesNotExist:
            context_data = {"education_form":""}
            education_form = EducationForm(prefix = 'education_form')
            context_data["education_form"] = education_form
            return render(request, "education.html", context_data)
        # education_form = EducationForm(request.GET, prefix = 'education_form')
        # print request.GET
        if request.user.is_authenticated:
            user = request.user
            employee = Education.objects.get(employee=request.user)
            qualification = employee.qualification
            specialization = employee.specialization
            from_date = employee.from_date
            to_date = employee.to_date
            institute = employee.institute
            overall_marks = employee.overall_marks
            marks_card_attachment = employee.marks_card_attachment
            education_form = EducationForm(initial = {'from_date':employee.from_date,'qualification':employee.qualification,'specialization':employee.specialization,
            'from_date':employee.from_date,'to_date':employee.to_date,'institute':employee.institute,
            'overall_marks':employee.overall_marks,'marks_card_attachment':employee.marks_card_attachment})

            context_data["education_form"] = education_form
            return render(request, "education.html", context_data)

    if request.method == 'POST':
        import ipdb; ipdb.set_trace()
        print request.POST
        education_form = EducationForm(request.POST, request.FILES, prefix = 'education_form')
        context_data = {"education_form":""}
        marks_card_attachment = request.FILES.get('marks_card_attachment',"")

        if education_form.is_valid():
            employee = User.objects.get(username=request.user)
            qualification = education_form.cleaned_data['qualification']
            specialization = education_form.cleaned_data['specialization']
            from_date = education_form.cleaned_data['from_date']
            to_date = education_form.cleaned_data['to_date']
            institute = education_form.cleaned_data['institute']
            overall_marks = education_form.cleaned_data['overall_marks']
            marks_card_attachment = education_form.cleaned_data['marks_card_attachment']
            if request.FILES.get('marks_card_attachment', ""):
                education_form.marks_card_attachment = request.FILES['marks_card_attachment']

            Education(employee=employee,
            qualification=qualification,
            specialization=specialization,
            from_date=from_date,
            to_date=to_date,
            institute=institute,
            overall_marks=overall_marks,
            marks_card_attachment=marks_card_attachment).save()
            context_data['education_form'] = education_form
            return render(request, 'education.html',context_data)

    context_data['education_form'] = education_form
    return render(request, 'education.html',context_data)

@csrf_exempt
@login_required

def proof(request):
    #proof form
    # context = {"form": ""}
    if request.method == 'GET':
        context = {"form":""}
        form = ProofForm()
        context["form"] = form
        # import ipdb; ipdb.set_trace()
        user = request.user
        try:
            employee = Proof.objects.get(employee=request.user)
        except Proof.DoesNotExist:
            context = {"form":""}
            form = ProofForm()
            context["form"] = form
            return render(request, "proof.html", context)

        pan = employee.pan
        pan_attachment = employee.pan_attachment
        aadhar_card = employee.aadhar_card
        aadhar_attachment = employee.aadhar_attachment
        dl = employee.dl
        dl_attachment = employee.dl_attachment
        passport = employee.passport
        passport_attachment = employee.passport_attachment
        voter_id = employee.voter_id
        voter_attachment = employee.voter_attachment

        form = ProofForm(initial = {'pan':employee.pan,'pan_attachment':employee.pan_attachment,
        'aadhar_card':employee.aadhar_card,'aadhar_attachment':employee.aadhar_attachment,'dl':employee.dl,
        'dl_attachment':employee.dl_attachment,'passport':employee.passport,'passport_attachment':employee.passport_attachment,
        'voter_id':employee.voter_id, 'voter_attachment':employee.voter_attachment})

        context["form"] = form
        return render(request, "proof.html", context)

    if request.method == 'POST':
        #import ipdb; ipdb.set_trace()
        context = {"form":""}
        form = ProofForm(request.POST, request.FILES)
        if form.is_valid():
            employee = User.objects.get(username=request.user)
            pan = form.cleaned_data['pan']
            pan_attachment = form.cleaned_data['pan_attachment']
            if request.FILES.get('pan_attachment', ""):
                form.pan_attachment = request.FILES['pan_attachment']
            aadhar_card = form.cleaned_data['aadhar_card']
            aadhar_attachment = form.cleaned_data['aadhar_attachment']
            if request.FILES.get('aadhar_attachment', ""):
                form.aadhar_attachment = request.FILES['aadhar_attachment']
            dl = form.cleaned_data['dl']
            dl_attachment = form.cleaned_data['dl_attachment']
            if request.FILES.get('dl_attachment', ""):
                form.dl_attachment = request.FILES['dl_attachment']
            passport = form.cleaned_data['passport']
            passport_attachment = form.cleaned_data['passport_attachment']
            if request.FILES.get('passport_attachment', ""):
                form.passport_attachment = request.FILES['passport_attachment']
            voter_id = form.cleaned_data['voter_id']
            voter_attachment = form.cleaned_data['voter_attachment']
            if request.FILES.get('voter_attachment', ""):
                form.voter_attachment = request.FILES['voter_attachment']

            Proof(employee=employee,
            pan=pan,
            pan_attachment=pan_attachment,
            aadhar_card=aadhar_card,
            aadhar_attachment=aadhar_attachment,
            dl=dl,
            dl_attachment=dl_attachment,
            passport=passport,
            passport_attachment=passport_attachment,
            voter_id=voter_id,
            voter_attachment=voter_attachment).save()
            context['form'] = form

            return HttpResponseRedirect("/myansrsource/user_details/confirm")

    context['form'] = form
    return render(request,'proof.html',context)

@csrf_exempt
@login_required
def previous_employment(request):
    #previous_employment form

    if request.method == 'GET':
        context = {"form":""}
        form = PreviousEmploymentForm()
        context["form"] = form
        #import ipdb; ipdb.set_trace()
        user = request.user
        try:
            employee = PreviousEmployment.objects.get(employee=request.user)
        except PreviousEmployment.DoesNotExist:
            context = {"form":""}
            form = PreviousEmploymentForm()
            context["form"] = form
            return render(request, "previous.html", context)
    #import ipdb; ipdb.set_trace()

    if request.method == 'POST':
        # import ipdb; ipdb.set_trace()

        form = PreviousEmploymentForm(request.POST, request.FILES)
        context = {"form":""}
        ps_attachment = request.FILES.get('ps_attachment',"")
        #rl_attachment = request.FILES.get('rl_attachment',"")

        if form.is_valid():
            employee = User.objects.get(username=request.user)
            company_name = form.cleaned_data['company_name']
            company_address = form.cleaned_data['company_address']
            job_type = form.cleaned_data['job_type']
            employed_from = form.cleaned_data['employed_from']
            employed_upto = form.cleaned_data['employed_upto']
            last_ctc = form.cleaned_data['last_ctc']
            reason_for_exit = form.cleaned_data['reason_for_exit']
            ps_attachment = form.cleaned_data['ps_attachment']
            if request.FILES.get('ps_attachment', ""):
                form.ps_attachment = request.FILES['ps_attachment']
            rl_attachment = form.cleaned_data['rl_attachment']
            if request.FILES.get('rl_attachment', ""):
                form.rl_attachment = request.FILES['rl_attachment']

            PreviousEmployment(employee=employee,
            company_name=company_name,
            company_address=company_address,
            job_type=job_type,
            employed_from=employed_from,
            employed_upto=employed_upto,
            last_ctc=last_ctc,
            reason_for_exit=reason_for_exit,
            ps_attachment=ps_attachment,
            rl_attachment=rl_attachment).save()
            context['form'] = form
            return render(request, 'previous.html',context)

    context['form'] = form
    return render(request, 'previous.html',context)

@csrf_exempt
@login_required
def confirm(request):
    #previous_employment form
    if request.user.is_authenticated:

        if request.method == 'GET':
            import ipdb; ipdb.set_trace()
            context = {'add':True, 'record_added':False, 'form':None}
            form = UserDetailsForm()
            # if request.user.is_authenticated():
            #     username = request.user.username
            user = request.user

            employee = UserDetails.objects.get(employee=user)
            first_name = user.first_name
            last_name = user.last_name
            middle_name = employee.middle_name
            nationality = employee.nationality
            marital_status = employee.marital_status
            wedding_date = employee.wedding_date
            blood_group = employee.blood_group
            land_phone = employee.land_phone
            emergency_phone = employee.emergency_phone
            mobile_phone = employee.mobile_phone
            personal_email = employee.personal_email
            gender = employee.gender

            context = {
            'employee':employee,
            'first_name':first_name,
            'last_name':last_name,
            'middle_name':middle_name,
            'nationality':nationality,
            'marital_status':marital_status,
            'wedding_date':wedding_date,
            'blood_group':blood_group,
            'land_phone':land_phone,
            'emergency_phone':emergency_phone,
            'mobile_phone':mobile_phone,
            'personal_email':personal_email,
            'gender':gender,
            }

            context.update(csrf(request))
    #ontext = {'form':form}

            return render(request, 'confirm.html',context)
    else:
        return HttpResponseRedirect('/myansrsource/login')

# @csrf_exempt
# @login_required
# def file(request):
#     # proof form
#     # context = {"form": ""}
#     if request.method == 'GET':
#         context = {"form":""}
#         form = FileUploadForm(request.GET)
#
#     if request.method == 'POST':
#         import ipdb; ipdb.set_trace()
#
#         form = FileUploadForm(request.POST, request.FILES)
#         context = {"form":""}
#         attachment = request.FILES.get('attachment', "")
#
#         if form.is_valid():
#             employee = User.objects.get(username=request.user)
#             title = form.cleaned_data['title']
#             attachment = form.cleaned_data['attachment']
#             if request.FILES.get('attachment', ""):
#                 form.attachment = request.FILES['attachment']
#
#             FileUpload(employee=employee,
#             title=title,
#             attachment=attachment).save()
#             context['form'] = form
#
#             return render(request,'file.html',context)
#
#     context['form'] = form
#
#     return render(request,'file.html',context)

def download_form(request):
    return render(request, 'download_forms.html',{})