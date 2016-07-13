from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from employee.models import Employee
import datetime, os


LEAVE_TYPES_CHOICES = (('earned_leave', 'Earned Leave'), ('sick_leave', 'Sick Leave'), ('casual_leave', 'Casual Leave'), ('loss_of_pay', 'Loss Of Pay'), ('bereavement_leave', 'Bereavement Leave'), ('maternity_leave', 'Maternity Leave'), ('paternity_leave', 'Paternity Leave'), ('comp_off_earned', 'Comp Off Earned'), ('comp_off_avail', 'Comp Off Avail'),('pay_off', 'Pay Off'), ('work_from_home', 'Work From Home'), ('sabbatical', 'Sabbatical'))
OCCURRENCE_CHOICES = (('monthly', 'Monthly'), ('yearly', 'Yearly'), ('none', 'None'))
CARRY_FORWARD_CHOICES = (('monthly', 'Monthly'), ('yearly', 'Yearly'), ('none', 'None'))
APPLICATION_STATUS = (('open', 'Open'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled'))
SESSION_STATUS = (('session_first', 'First Half'), ('session_second', 'Second Half'))
BUTTON_NAME = (('success', 'approved'), ('info', 'open'), ('danger', 'rejected'), ('warning', 'cancelled'))

# def content_file_name(instance, filename):
#     return '/'.join(['content', instance.user.username, filename])

def content_file_name(instance, filename):
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
    path = "leaves/uploads/" + str(datetime.datetime.now().year) + "/" + str(datetime.datetime.now().month) + "/" + str(datetime.datetime.now().day) + "/"
    os_path = os.path.join(path, filename)
    return os_path

class LeaveType(models.Model):
    ''' This model contains :
    leave types,
    occurrence : monthly/yearly,
    count : based on occurrence.
    carry_forward : yearly/no,
    effective_from : date
    '''

    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPES_CHOICES, verbose_name='Leave Types')
    occurrence = models.CharField(max_length=10, choices=OCCURRENCE_CHOICES, verbose_name='changes monthly or yearly')
    count = models.CharField(max_length=20, verbose_name='Number of Leaves')
    carry_forward = models.CharField(max_length=10, choices=CARRY_FORWARD_CHOICES, verbose_name='carry forward choices')
    effective_from = models.DateField(verbose_name='date of effect')
    apply_within_days = models.CharField(max_length=10, verbose_name='days limit for applying')

    def __unicode__(self):
       ''' return unicode strings '''
       return '%s' % (self.leave_type)

class LeaveSummary(models.Model):
    user = models.ForeignKey(User, verbose_name='User')
    year = models.CharField(max_length=10, verbose_name='Current Year')
    leave_type = models.ForeignKey(LeaveType, verbose_name='Leave Type')
    applied = models.CharField(max_length=20, verbose_name='applied leave count')
    approved = models.CharField(max_length=20, verbose_name='approved leave count')
    balance = models.CharField(max_length=20, verbose_name='balance leave count')


    def __unicode__(self):
       ''' return unicode strings '''
       return '%s' % (self.user.username)

    # class Meta:
    #     unique_together = ('user', 'leave_type')

class LeaveApplications(models.Model):

    ''' This model contains all the details reated to the leave application. Some of the fields are:
    status : open/approved/rejeted/cancelled
    status_action_by : the user who approved/cancelled/rejected the leave application
    status_action_on : date on which the above action was taken
    status_comments : this contains the reason for the action taken. eg. reason for rejection/cancellation of the application
    due_date : date till which the application is due. eg. comp off or payoff due date will be say 90 days after which the employee cannot apply for
    '''

    user = models.ForeignKey(User, db_index=True, verbose_name='User', related_name='user') #- i
    leave_type = models.ForeignKey(LeaveType, db_index=True, verbose_name='Leave Type') #- i
    from_date = models.DateField(verbose_name='Leave from Date')
    from_session = models.CharField(max_length=20, choices=SESSION_STATUS, verbose_name='')
    to_date = models.DateField(verbose_name='Leave to Date')
    to_session = models.CharField(max_length=20, choices=SESSION_STATUS, verbose_name='')
    apply_to = models.ForeignKey(User, db_index=True, verbose_name='Manager', related_name='manager') #- i
    reason = models.CharField(max_length=1000, verbose_name='Reason',blank=True, null=True,)
    status = models.CharField(max_length=100, choices=APPLICATION_STATUS, verbose_name='Status Of Leave')
    status_action_by = models.ForeignKey(User, verbose_name='Change By User', related_name='applied_by')
    status_action_on = models.DateField(auto_now=True, verbose_name='Date of Change')
    status_comments = models.CharField(max_length=500, verbose_name='Status change comment')
    due_date = models.DateField(verbose_name='application of comp off', null=True)#for comp off date
    days_count = models.CharField(max_length=10, verbose_name='Leave Count')
    atachement = models.FileField(upload_to=content_file_name, blank=True, null=True, verbose_name='Attachment')
    applied_on = models.DateField(auto_now_add=True, verbose_name='Leave Applied Date')
    modified_on = models.DateField(auto_now=True, verbose_name='Modified Date')
    active = models.BooleanField(blank=False, default=True, verbose_name="Is Active?")

    def __unicode__(self):
      ''' return unicode strings '''
      return '%s' % (self.user.username)

    def saveas(self, user, *args, **kwargs):
        manager_id = Employee.objects.filter(user_id=user).values('manager_id')
        manager = Employee.objects.filter(employee_assigned_id=manager_id).values('user_id')
        manager_d = User.objects.get(id=manager[0]['user_id'])
        self.user = User.objects.get(id=user)
        self.apply_to = manager_d
        self.status = 'open'
        self.status_action_by = User.objects.get(id=user)
        self.status_comments = "submitted"
        super(LeaveApplications, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        super(LeaveApplications, self).save(*args, **kwargs)
