from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


# Create your models here.

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

    def __unicode__(self):
        return self.User

    class Meta:
        verbose_name = 'Regignation info'

'''Database for clearance from all Dept...'''


class ClearanceInfo(models.Model):
    resign = models.ForeignKey(User)
    hr_clearance = models.BooleanField(verbose_name="hr clearance", blank=True)
    IT_clearance = models.BooleanField(verbose_name="it clearance", blank=True)
    manager_clearance = models.BooleanField(verbose_name="manager clearance", blank=True)
    admin_clearance = models.BooleanField(verbose_name="admin clearance", blank=True)
    library_clearance = models.BooleanField(verbose_name="Library clearance", blank=True)

    def __unicode__(self):
        return self.resign


'''Model for storing the employee feedback'''


class EmployeeFeedback(models.Model):
    employee_id = models.ForeignKey(User)
    hr_feedback = models.CharField(verbose_name="HR comment over Employee", blank=False, max_length=1000)
    manager_feedback = models.CharField(verbose_name="Manger comment over Employee", blank=False, max_length=1000)
    it_feedback = models.CharField(verbose_name="IT comment over Employee", blank=False, max_length=1000)
    library_feedback = models.CharField(verbose_name="LIBRARY comment over Employee", blank=False, max_length=1000)
    admin_feedback = models.CharField(verbose_name="HR comment over Employee", blank=False, max_length=1000)




