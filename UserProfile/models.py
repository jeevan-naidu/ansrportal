from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from employee.models import Designation, Employee
from CompanyMaster.models import OfficeLocation


# Create your models here.

class MyProfile(models.Model):

	user = models.ForeignKey(User)
	location = models.ForeignKey(OfficeLocation)
	designation = models.ForeignKey(Designation)

	def __unicode__(self):
		return '%s' % (self.user)