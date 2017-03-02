from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from employee.models import Employee


# Create your models here.
class Skill_Lists(models.Model):
    # User = models.ForeignKey(User, unique=True)

    skill_name = models.CharField(verbose_name="Skill Name", max_length=100)
    level1 = models.CharField(verbose_name="Level1", max_length=500)
    level2 = models.CharField(verbose_name="Level2", max_length=500)
    level3 = models.CharField(verbose_name="Level3", max_length=500)

    def __unicode__(self):
        return unicode(self.skill_name)

    class Meta:
        verbose_name = 'Skill List'


class User_Skills(models.Model):
    skill_id = models.ForeignKey(Skill_Lists, verbose_name="Skill ID")
    employee_id = models.ForeignKey(Employee, verbose_name="Employee ID")
    skill_name = models.CharField(max_length=500, verbose_name="Skill Name")
    skill_type = models.CharField(max_length=500, verbose_name="Skill Type")
    is_status = models.CharField(max_length=200, verbose_name="Is Status")
    createdon = models.DateTimeField(verbose_name="created Date", auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date", auto_now_add=True)

    def __unicode__(self):
        return u'{0},{1}'.format(self.skill_id, self.employee_id)

    class Meta:
        verbose_name = 'User Skills'
