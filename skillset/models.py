from __future__ import unicode_literals

from django.db import models
from datetime import datetime

SKILL_LEVEL=(
    ('L1', 'Level 1'), ('L2', 'Level 2'), ('L3', 'Level 3')
)

# Create your models here.
class Skill_Lists(models.Model):
    # User = models.ForeignKey(User, unique=True)

    skill_name = models.CharField(verbose_name="Skill Name", max_length=100)
    level1 = models.TextField(verbose_name="Level1", max_length=2000)
    level2 = models.TextField(verbose_name="Level2", max_length=2000)
    level3 = models.TextField(verbose_name="Level3", max_length=2000)

    def __unicode__(self):
        return unicode(self.skill_name)


    class Meta:
        verbose_name = 'Skill List'


class User_Skills(models.Model):

    sid = models.IntegerField(primary_key=True, default=0)
    emp_mid = models.CharField(max_length=20, verbose_name="Employee ID", default="")
    skills_name = models.CharField(verbose_name="Skill Name", max_length=300, default="")
    skills_type = models.CharField(max_length=10, verbose_name="Skill Level", default="")
    create_date = models.DateTimeField(verbose_name="created Date", default=datetime.now, blank=True)
    update_date = models.DateTimeField(verbose_name="Updated Date", default=datetime.now, blank=True)

    def __unicode__(self):
        return u'{0},{1}'.format(self.skills_name, self.skills_type)

    class Meta:
        verbose_name = 'User Skills'
