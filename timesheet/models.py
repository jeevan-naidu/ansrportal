from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=50)

class TSEntry(models.Model):
    project = models.ForeignKey(Project)
    wkstart = models.DateField(verbose_name = 'Week Start', auto_now_add = True)
    wkend = models.DateField(verbose_name = 'Week Ending', auto_now_add = True)
    monday = models.IntegerField(default=0)
    approved = models.BooleanField(default=False)


class ProjectChangeInfo(models.Model):
    project = models.ForeignKey(Project)
    changed_on = models.DateField(auto_now_add = True)
    cr_id = models.CharField(default=None, blank = True, max_length=100)
    reason = models.CharField(max_length=100)
    end_date = models.DateField(verbose_name = 'Revised Project End Date', auto_now_add = True, null=True, blank=True)
    revised_effort = models.IntegerField(default=0)
    approved = models.BooleanField(default=False)


class ProjectMilestones(models.Model):
    project = models.ForeignKey(Project)
    milestone_date = models.DateField(verbose_name = 'Milestone Date', default=None, auto_now_add = True)
    description = models.CharField(default=None, blank=True, max_length=100)


class ProjectTeam(models.Model):
    project = models.ForeignKey(Project)
    member = models.ForeignKey(User)
