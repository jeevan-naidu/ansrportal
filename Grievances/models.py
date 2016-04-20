from django.db import models
from django.contrib.auth.models import User
import datetime, os
from employee.models import TeamMember

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from django.core.validators import MinLengthValidator
from django.utils.safestring import mark_safe


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



class Grievances_category(models.Model):
    
    category = models.CharField(max_length=200)
    active = models.BooleanField(blank=False, default=True, verbose_name="Is Active?")
    
    def __unicode__(self):
        ''' return unicode strings '''
        return '%s' % (self.category)

class Grievances(models.Model):
    user = models.ForeignKey(User)
    
    grievance_id = models.CharField(max_length=60, unique=True)
    category = models.ForeignKey(Grievances_category)
    subject = models.CharField(max_length=100, validators=[MinLengthValidator(15)])
    
    # length validations are different for front-end and backend. e.g js treats new line as 1 character and python treats the same as "\n" i.e 2
    #characters. So to be safe, we are giving length 200 characters more than what is validated in front-end(2000 characters)
    grievance = models.TextField(max_length=2200, validators=[MinLengthValidator(15)], help_text=mark_safe("<span id='textarea_remaining'>2000 remaining</span>"))
    
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
        """ return unicode strings """
        return '%s' % (self.grievance_id)
    
    class Meta:
        verbose_name_plural = "Grievances"
