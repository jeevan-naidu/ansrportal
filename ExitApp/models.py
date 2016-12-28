from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User



# Create your models here.

EMP_AMOUNT = (
    ('IT', 'IT Support'),
    ('FIN', 'Finance'),
    ('LIB', 'Library'),
    ('FAC', 'Facility'),
    ('HR', 'Human Resource')

)


EMP_FEEDBACK = (
    ('IT', 'IT Support'),
    ('FIN', 'Finance'),
    ('LIB', 'Library'),
    ('FAC', 'Facility'),
    ('HR', 'Human Resource')
)

'''Table to store the data of employee who is exiting the organization'''


class ResignationInfo(models.Model):
    User = models.ForeignKey(User, unique=True)
    emp_reason = models.CharField(verbose_name="Reason", blank=False, max_length=250,)
    hr_accepted = models.NullBooleanField (verbose_name="HR clearance", null=True, blank=True)
    manager_accepted = models.NullBooleanField (verbose_name="manager clearance", null=True, blank=True)
    last_date = models.DateTimeField(verbose_name="Last Date Opted By employee", blank=True)
    last_date_accepted = models.DateTimeField(verbose_name="Last Date Accepted By Organisation", blank=True, null=True)
    reason_optional = models.CharField(verbose_name="optional text area", blank=True, max_length=1000,)
    created_on = models.DateTimeField(verbose_name="created on", auto_now_add=True)
    updated_on = models.DateTimeField(verbose_name="updated on", auto_now_add=True)
    # is_active = models.NullBooleanField(verbose_name="If employee left", blank=True)

    def __unicode__(self):
        return unicode(self.User)

    class Meta:
        verbose_name = 'Regignation info'

'''Database for clearance from all Dept...'''


class EmployeeClearanceInfo(models.Model):
    resignationInfo = models.ForeignKey(ResignationInfo)
    dept_status = models.BooleanField(verbose_name="Clearance from Department", blank=True)
    status_by = models.ForeignKey(User, unique=True)
    status_on = models.DateTimeField(verbose_name = "Time of Approval")
    dept_feedback = models.CharField(
        max_length=1000,
        choices=EMP_FEEDBACK,
        blank=True)
    dept_due = models.IntegerField(
        choices=EMP_AMOUNT,
        blank=True
    )








