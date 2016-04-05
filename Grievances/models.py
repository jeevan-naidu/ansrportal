from django.db import models
from django.contrib.auth.models import User
import datetime, os
from employee.models import TeamMember

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from django.core.validators import MinLengthValidator


SATISFACTION_CHOICES = (('satisfied', 'Satisfied'), ('not_sure', 'Not Sure'), ('dissatisfied', 'Dissatisfied'), ('very_dissatisfied', 'Very Dissatisfied') )
STATUS_CHOICES = (('new', 'New'), ('opened', 'Opened'), ('in_progress', 'In Progress'))
STATUS_CHOICES_CLOSED = (('new', 'New'), ('opened', 'Opened'), ('in_progress', 'In Progress'), ('closed', 'Closed'))

def change_file_path(instance, filename):
    
    ''' This function generates a random string of length 16 which will be a combination of (4 digits + 4
    characters(lowercase) + 4 digits + 4 characters(uppercase)) seperated 4 characters by hyphen(-) '''
    
    import random
    import string
    
    # random_str length will be 16 which will be combination of (4 digits + 4 characters + 4 digits + 4 characters)
    random_str =  "".join([random.choice(string.uppercase) for i in range(0,4)]) + "".join([random.choice(string.digits) for i in range(0,4)]) + \
                    "".join([random.choice(string.lowercase) for i in range(0,4)]) + "".join([random.choice(string.digits) for i in range(0,4)])
    
    # return string seperated by hyphen eg:
    random_str =  random_str[:4] + "-" + random_str[4:8] + "-" + random_str[8:12] + "-" + random_str[12:]
    filetype = filename.split(".")[-1].lower()
    filename = random_str +"." +  filetype
    path = "grievances/uploads/" + str(datetime.datetime.now().year) + "/" + str(datetime.datetime.now().month) + "/" + str(datetime.datetime.now().day) + "/"
    os_path = os.path.join(path, filename)
    return os_path



class Grievances_catagory(models.Model):
    
    catagory = models.CharField(max_length=200)
    active = models.BooleanField(blank=False, default=True, verbose_name="Is Active?")
    
    def __unicode__(self):
        ''' return unicode strings '''
        return '%s' % (self.catagory)

class Grievances(models.Model):
    user = models.ForeignKey(User)
    
    grievance_id = models.CharField(max_length=60, unique=True)
    catagory = models.ForeignKey(Grievances_catagory)
    subject = models.CharField(max_length=100, validators=[MinLengthValidator(15)])
    grievance = models.TextField(max_length=2000, validators=[MinLengthValidator(15)])
    
    action_taken = models.TextField(max_length = 2000, blank=True, null=True, validators=[MinLengthValidator(15)])
    user_closure_message = models.TextField(max_length = 2000, blank=True, null=True, validators=[MinLengthValidator(5)])
    admin_closure_message = models.TextField(max_length = 2000, blank=True, null=True, validators=[MinLengthValidator(5)])
    
    satisfaction_level = models.CharField(max_length = 50, blank=True, null=True, choices=SATISFACTION_CHOICES)
    
    escalate = models.BooleanField(default=False)
    escalate_to = models.CharField(max_length=200, blank=True, null=True, help_text="In case of multiple email id's, seperate them by a semicolan. Do not use single or double quotes anywhere")
    
    grievance_attachment  = models.FileField(upload_to=change_file_path, blank=True, null=True)
    admin_action_attachment = models.FileField(upload_to=change_file_path, blank=True, null=True)
    user_closure_message_attachment = models.FileField(upload_to=change_file_path, blank=True, null=True)
    admin_closure_message_attachment = models.FileField(upload_to=change_file_path, blank=True, null=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    action_taken_date = models.DateTimeField(blank=True, null=True)
    admin_closure_message_date = models.DateTimeField(blank=True, null=True)
    
    closure_date = models.DateTimeField(blank=True, null=True)
    
    active = models.BooleanField(blank=False, default=True, verbose_name="Is Active?")
    grievance_status = models.CharField(max_length=50, blank=False, null=False, default="new", choices=STATUS_CHOICES)
    
    def __unicode__(self):
        ''' return unicode strings '''
        return '%s' % (self.id)
    
    class Meta:
        verbose_name_plural="Grievances"
        
  
    
    # Send mails.
    # This method should be removed after seperate admin backend is deployed
    def save(self, *args, **kwargs):
        
        if self.id:
            database_object = Grievances.objects.get(id=self.id)
           
            if database_object.escalate_to is None:
                database_object.escalate_to = "" # bcoz for next line if self.escalte_to is empty string from form, then we cant compare none type and empty string, so make 'None' to empty string
            if database_object.escalate_to != self.escalate_to:
                EscalateToList = self.escalate_to.replace("'","").replace('"', '').split(";")
                msg_html = render_to_string('email_templates/EscalateToTemplate.html', {'registered_by': database_object.user.first_name, 'grievance_id':database_object.grievance_id, 'grievance_subject':database_object.subject})
                mail_obj = EmailMessage('Escalation - Grievance Id - ' + database_object.grievance_id, msg_html, settings.EMAIL_HOST_USER, EscalateToList, cc=[settings.GRIEVANCES_ADMIN_EMAIL])
                mail_obj.content_subtype = 'html'
                email_status = mail_obj.send()
                
                if email_status < 1:
                    # TODO  - mail not sent, log this error
                    pass
                
            if not database_object.action_taken and self.action_taken :
                # this means the HR has taken action on the grievance. Send mails to the HR as well as the employee and update the date
                
                msg_html = render_to_string('email_templates/ActionTakenTemplate.html', {'registered_by': database_object.user.first_name, 'grievance_id':database_object.grievance_id, 'grievance_subject':database_object.subject})
                mail_obj = EmailMessage('Action taken - Grievance Id - ' + database_object.grievance_id, msg_html, settings.EMAIL_HOST_USER, [database_object.user.email], cc=[settings.GRIEVANCES_ADMIN_EMAIL])
                mail_obj.content_subtype = 'html'
                email_status = mail_obj.send()
                
                if email_status < 1:
                    # TODO  - mail not sent, log this error
                    pass
                self.action_taken_date = datetime.datetime.now()
                
            elif database_object.action_taken != self.action_taken:
                # this means the HR has edited/changed the action taken field. Send update mails to the HR as well as the employee and update the date
                msg_html = render_to_string('email_templates/EditActionTakenTemplate.html', {'registered_by': database_object.user.first_name, 'grievance_subject':database_object.subject})
                mail_obj = EmailMessage('Change in action taken - Grievance Id - ' + database_object.grievance_id, msg_html, settings.EMAIL_HOST_USER, [database_object.user.email], cc=[settings.GRIEVANCES_ADMIN_EMAIL])
                mail_obj.content_subtype = 'html'
                email_status = mail_obj.send()
                if email_status < 1:
                    # TODO  - mail not sent, log this error
                    pass
                self.action_taken_date = datetime.datetime.now()
            
            if database_object.admin_closure_message is None:
                database_object.admin_closure_message = "" # bcoz for next line if self.admin_closure_message is empty string coming from form, then we cant compare none type and empty string, so make 'None' to empty string
            
            if database_object.admin_closure_message == "" and self.admin_closure_message:
                # this mmeans the HR has added the closure message. Send mails to HR and the user and update the date.
                msg_html = render_to_string('email_templates/AdminClosureMessageTemplate.html', {'registered_by': database_object.user.first_name, 'grievance_subject':database_object.subject})
                mail_obj = EmailMessage('HR Message - Grievance  Id - ' + database_object.grievance_id, msg_html, settings.EMAIL_HOST_USER, [self.user.email], cc=[settings.GRIEVANCES_ADMIN_EMAIL])
                mail_obj.content_subtype = 'html'
                email_status = mail_obj.send()
                if email_status < 1:
                    # TODO  - mail not sent, log this error
                    pass
                self.admin_closure_message_date = datetime.datetime.now()
              
            elif database_object.admin_closure_message != self.admin_closure_message:
                # this means HR has edited/changed the closure message. Send update mails to the HR aas well as the employee and update the date field.
                msg_html = render_to_string('email_templates/EditAdminClosureMessageTemplate.html', {'registered_by': database_object.user.first_name, 'grievance_subject':database_object.subject})
                mail_obj = EmailMessage('Change in admin message - Grievance Id - ' + database_object.grievance_id, msg_html, settings.EMAIL_HOST_USER, [database_object.user.email], cc=[settings.GRIEVANCES_ADMIN_EMAIL])
                mail_obj.content_subtype = 'html'
                email_status = mail_obj.send()
                if email_status < 1:
                    # TODO  - mail not sent, log this error
                    pass
                
                self.admin_closure_message_date = datetime.datetime.now()
                
       
                
            elif database_object.active == False and self.active == True:
                # this means the HR wants to reopen this grievance. Send mails to HR and the employee
                msg_html = render_to_string('email_templates/OpenClosedGrievanceMessageTemplate.html', {'registered_by': database_object.user.first_name, 'grievance_subject':database_object.subject})
                mail_obj = EmailMessage('Closed grievance opened - Id - ' + database_object.grievance_id, msg_html, settings.EMAIL_HOST_USER, [database_object.user.email], cc=[settings.GRIEVANCES_ADMIN_EMAIL])
                mail_obj.content_subtype = 'html'
                email_status = mail_obj.send()
                if email_status < 1:
                    # TODO  - mail not sent, log this error
                    pass
        
        super(Grievances, self).save(*args, **kwargs) # Call the "real" save() method.
    
  

    