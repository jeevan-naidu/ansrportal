from django.db import models
from django.contrib.auth.models import User

REFERENCE_SOURCE = (('naukari', 'Naukari'), ('linkedin', 'Linkedin'), ('career', 'Career'),
                    ('employee_referral', 'Employee Referral'),('others', 'Others'))
RESULT_STATUS = (('rejected', 'Rejected'), ('on_hold', 'On Hold'), ('selected', 'Selected'))
INTERVIEW_PROCESS = (('test', 'Test'), ('f2f', 'Face To Face'),('others', 'Others'))
GENDER_CHOICES = (('male', 'Male'),('female', 'Female'))

class Position(models.Model):
    '''
    This table stores position avaliable in comapany
    '''
    department = models.CharField(max_length=50, verbose_name='Department')
    designation = models.CharField(max_length=50, verbose_name='Designation')
    specialization = models.CharField(max_length=50, verbose_name='Specializtion')

    def __unicode__(self):
        return '%s' % self.department


class MRF(models.Model):
    '''
    This model is used for storing detail of
    MRF.
    '''
    requisition_number = models.CharField(max_length=50)
    position = models.ForeignKey(Position, related_name='position')
    manager = models.ForeignKey(User, verbose_name='manager raising MRF', related_name='recruit_manager')
    created_on = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return '%s' % self.requisition_number


class Count(models.Model):
    '''
    This model is used for storing the count of certain
    requsition number divided between recruiter.
    '''
    requisition_number = models.ForeignKey(MRF)
    recruiter = models.ForeignKey(User, verbose_name='Hr alotted for recruitment process', related_name='hire_hr')
    count = models.IntegerField(default=0, verbose_name='count of candidate recruit by hr')

    def __unicode__(self):
        return '%s' % self.recruiter.first_name + " " + self.requisition_number.requisition_number


class Profile(models.Model):
    '''
    This model is used for storing candidates details,
    who all are coming for interview.
    '''
    candidate_name = models.CharField(max_length=50, verbose_name='Candidate Name')
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, verbose_name='Gender')
    mobile_number = models.CharField(max_length=15)
    email_id = models.EmailField(max_length=254, null=True)
    requisition_number = models.ForeignKey(Count, verbose_name='Requsition Number', related_name='mrf_no')
    source = models.CharField(max_length=50, choices=REFERENCE_SOURCE, verbose_name='')
    referred_by = models.ForeignKey(User, null=True, blank=True, verbose_name='Referred By',related_name='employee_refered')
    candidate_status = models.CharField(max_length=50, choices=RESULT_STATUS, verbose_name='Final Status')
    active = models.BooleanField(null=False, default=True)
    created_on = models.DateField(auto_now_add=True)
    modified_on = models.DateField(auto_now=True)

    def __unicode__(self):
        return '%s' % self.candidate_name



class Process(models.Model):
    '''
    This model is used for storing interview process
    for a certain candidates.
    '''
    interview_step = models.CharField(max_length=50, choices=INTERVIEW_PROCESS, verbose_name='Interview Process Name')
    interview_status = models.CharField(max_length=50, choices=RESULT_STATUS, verbose_name='process status')
    interview_by = models.ManyToManyField(User, verbose_name='Interviewers')
    interview_on = models.DateField()
    profile = models.ForeignKey(Profile, verbose_name='Candidate Name', related_name='candidate')
    feedback = models.TextField(verbose_name='Feedback')
    created_on = models.DateField(auto_now_add=True)
    modified_on = models.DateField(auto_now=True)

    def __unicode__(self):
        return '%s' % self.profile.candidate_name




