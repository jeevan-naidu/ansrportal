from django.shortcuts import render
from django.views.generic import View
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from forms import AddGrievanceForm
from Grievances.models import Grievances, SATISFACTION_CHOICES
from django.http import JsonResponse
import datetime
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

AllowedFileTypes = ['jpg', 'csv','png', 'pdf', 'xlsx', 'xls', 'docx', 'doc', 'jpeg', 'eml']

def generate_random_string():
    ''' This function generates a random string of length 16 which will be a combination of (4 digits + 4
    characters(lowercase) + 4 digits + 4 characters(uppercase)) seperated 4 characters by hyphen(-) '''
    
    import random
    import string
    
    # random_str length will be 16 which will be combination of (4 digits + 4 characters + 4 digits + 4 characters)
    random_str =  "".join([random.choice(string.digits) for i in range(0,4)]) + "".join([random.choice(string.lowercase) for i in range(0,4)]) + \
                    "".join([random.choice(string.digits) for i in range(0,4)]) + "".join([random.choice(string.uppercase) for i in range(0,4)])
    
    # return string seperated by hyphen eg:
    return random_str[:4] + "-" + random_str[4:8] + "-" + random_str[8:12] + "-" + random_str[12:]


class GrievancesListView(ListView):

    def get(self, request):
        objects_list = Grievances.objects.filter(user=self.request.user).order_by("-created_date")
        return render(request, 'grievances_list.html', {'objects_list':objects_list, 'satisfaction_choices':SATISFACTION_CHOICES})

class AddGrievanceView(View):
    ''' add or edit grievances '''
    
    
    def get(self, request):
        
        context_data = {'add':True, 'record_added':False, 'form':None}
        form = AddGrievanceForm()
        context_data['form'] = form
        return render(request, 'add_grievance.html', context_data)
    
    def post(self, request):
        
        form = AddGrievanceForm(request.POST, request.FILES)
        response_data = {}
        context_data = {'add' : True, 'record_added' : False, 'form' : None, 'success_msg' : None, 'html_data' : None, 'errors' : [] }
        if request.FILES.get('grievance_attachment', ""):
            if request.FILES['grievance_attachment'].name.split(".")[-1] not in AllowedFileTypes:
                context_data['errors'].append('Attachment : File type not allowed. Please select a valid file type and then submit again')
        if form.is_valid() and not context_data['errors']:
            form = form.save(commit=False)
            if not form.user_id:
                form.user = request.user
            form.grievance_id = generate_random_string()
            if request.FILES.get('grievance_attachment', ""):
                form.grievance_attachment = request.FILES['grievance_attachment']
            form.save()
            
            context_data['record_added'] = 'True'
            context_data['object'] = Grievances.objects.get(id=form.id)
            
            # Send e-mails
            msg_html = render_to_string('email_templates/NewGrievanceTemplate.html', {'registered_by': request.user.first_name, 'grievance_id':form.grievance_id, 'grievance_subject':form.subject})
            
            mail_obj = EmailMessage('New Grievance Registered- Grievance Id - ' + form.grievance_id, msg_html, settings.EMAIL_HOST_USER, [request.user.email], cc=[settings.GRIEVANCES_ADMIN_EMAIL])
            mail_obj.content_subtype = 'html'
            email_status = mail_obj.send()
            
            if email_status < 1:
                # TODO  - mail not sent, log this error
                pass
           
            
            context_data['success_msg'] = "Your grievance has been submitted successfully. A person from the HR department will get back to you shortly."
            template = render(request, 'add_grievance.html', context_data)
            context_data['html_data'] = template.content
            context_data.pop('object')   # remove non seriazable object
            return JsonResponse(context_data)
            
        else:
            context_data['form'] = form
        
        return render(request, 'add_grievance.html', context_data)


def RateAndCloseView(request):
    
    context_data = {'errors': [], 'record_added': False, 'object':"", 'success_data_template':""}
    if not request.POST.get('satisfaction_level', ''):
        context_data['errors'].append('Satisfaction Level: Please select one of the options for this field<br>')
    
    user_closure_message = request.POST.get('user_closure_message', '').strip()
    if not user_closure_message:
        context_data['errors'].append('Message: Please enter the message<br>')
    elif len(user_closure_message) > 2000:
        context_data['errors'].append('Message: Ensure that this field has atmost 2000 characters <br>')
        
    if request.FILES.get('user_closure_message_attachment', ""):
        if request.FILES['user_closure_message_attachment'].name.split(".")[-1] not in AllowedFileTypes:
            context_data['errors'].append('Attachment: File type not allowed <br>')
        
    if not context_data['errors']:
        grievance_obj = Grievances.objects.get(grievance_id=request.POST['grievance_id'])
        grievance_obj.satisfaction_level = request.POST['satisfaction_level']
        grievance_obj.user_closure_message = request.POST['user_closure_message'].strip()
        if request.FILES.get('user_closure_message_attachment', ""):
            grievance_obj.user_closure_message_attachment = request.FILES['user_closure_message_attachment']
        grievance_obj.closure_date = datetime.datetime.now()
        grievance_obj.active = False
        grievance_obj.grievance_status = 'closed'
        grievance_obj.save()
        
        # Send notification mails
        msg_html = render_to_string('email_templates/GrievanceClosedByUserMessageTemplate.html', {'registered_by': request.user.first_name , 'grievance_id':grievance_obj.grievance_id, 'grievance_subject':grievance_obj.subject,'satisfaction_level':grievance_obj.satisfaction_level})
        mail_obj = EmailMessage('Grievance Closed - Id - ' + grievance_obj.grievance_id, msg_html, settings.EMAIL_HOST_USER, [request.user.email], cc=[settings.GRIEVANCES_ADMIN_EMAIL])
        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        
        if email_status < 1:
            # TODO  - mail not sent, log this error
            pass
        
        context_data['record_added'] = True
        context_data['object'] = grievance_obj
        template  = render(request, 'submit_user_actions.html', context_data)
        context_data['success_data_template'] = template.content
        context_data.pop('object')   # remove non seriazable object
    
    return JsonResponse(context_data)

    

def EscalateGrievanceView(request):
    
    context_data = {'errors': [], 'record_added': False, 'success_message':""}
    grievance_obj = Grievances.objects.get(grievance_id=request.POST['grievance_id'])
    grievance_obj.escalate = True
    grievance_obj.save()
    
    msg_html = render_to_string('email_templates/EscalatedByUserMessageTemplate.html', {'registered_by': request.user.first_name , 'grievance_id':grievance_obj.grievance_id, 'grievance_subject':grievance_obj.subject})
    mail_obj = EmailMessage('Grievance Escalation - Id - ' + grievance_obj.grievance_id, msg_html, settings.EMAIL_HOST_USER, [request.user.email], cc=[settings.GRIEVANCES_ADMIN_EMAIL])
    mail_obj.content_subtype = 'html'
    email_status = mail_obj.send()
    if email_status < 1:
        # TODO  - mail not sent, log this error
        pass
    
    
    context_data['record_added'] = True
    context_data['success_message'] = "Your grievance is escalated to the concerned authorities. Stay cool.."
    return JsonResponse(context_data)
  
