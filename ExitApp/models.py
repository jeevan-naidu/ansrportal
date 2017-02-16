from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User



# Create your models here.

Department = (
    ('IT', 'IT Support'),
    ('FIN', 'Finance'),
    ('LIB', 'Library'),
    ('FAC', 'Facility'),
    ('HR', 'Human Resource'),
    ('MGR', 'Manager')
)

'''Table to store the data of employee who is exiting the organization'''


class ResignationInfo(models.Model):
    User = models.ForeignKey(User, unique=True)
    emp_reason = models.CharField(verbose_name="Reason", blank=False, max_length=250,)
    hr_accepted = models.NullBooleanField(verbose_name="HR clearance", null=True, blank=True)
    rehire_hr = models.NullBooleanField(verbose_name="HR Concent fo rehire", null=True, blank=True)
    rehire_manager = models.NullBooleanField(verbose_name="Manager Concent for rehire", null=True, blank=True)
    backup_taken = models.NullBooleanField(verbose_name="system Back up Taken or not ", null=True, blank=True)
    manager_accepted = models.NullBooleanField (verbose_name="manager clearance", null=True, blank=True)
    last_date = models.DateField(verbose_name="Last Date Opted By employee", blank=True)
    last_date_accepted = models.DateField(verbose_name="Last Date Accepted By Organisation", blank=True, null=True)
    reason_optional = models.CharField(verbose_name="optional text area", blank=True, max_length=1000,)
    created_on = models.DateTimeField(verbose_name="created on", auto_now_add=True, null=True)
    updated_on = models.DateTimeField(verbose_name="updated on", auto_now_add=True, null=True)
    manager_comment = models.CharField(verbose_name="Manager comment", null=True, blank=True, max_length=1000,)
    hr_comment = models.CharField(verbose_name="HR comment", null=True, blank=True, max_length=1000,)
    exit_interview_notes = models.CharField(verbose_name="Exit Interview Summary", null=True, blank=True, max_length=2000,)
    exit_interview_flag = models.NullBooleanField(verbose_name="Exit Interview Happened or Not", null=True, blank=True)
    exit_revert_flag = models.NullBooleanField(verbose_name="Resignation Withdraw ?", null=True, blank=True)
    exit_revert_note = models.CharField(verbose_name="Note for Reverting the resignation", null=True, blank=True, max_length=2000,)

    def __unicode__(self):
        return unicode(self.User)

    class Meta:
        verbose_name = 'Regignation info'


'''Database for clearance from all Dept...'''


class EmployeeClearanceInfo(models.Model):
    resignationInfo = models.ForeignKey(ResignationInfo)
    dept_status = models.BooleanField(verbose_name="Clearance from Department", blank=True)
    status_by = models.ForeignKey(User)
    department = models.CharField(verbose_name='Department', choices=Department, max_length=40, blank=False)
    status_on = models.DateField(verbose_name="Time of Approval")
    dept_feedback = models.CharField(max_length=1000, blank=True, verbose_name="Department Feedback")
    dept_due = models.IntegerField(verbose_name="Recovery Amount",  blank=True)

    def __unicode__(self):
        return unicode(self.department)

    class Meta:
        verbose_name = 'Employee Clearance Info'
        unique_together = ('department', 'resignationInfo')











