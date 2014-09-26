# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=None, max_length=50, verbose_name=b'Project Name', blank=True)),
                ('startDate', models.DateTimeField(default=None, verbose_name=b'Project Start Date', auto_now_add=True)),
                ('endDate', models.DateTimeField(default=None, verbose_name=b'Project End Date', auto_now_add=True)),
                ('plannedEffort', models.IntegerField(default=0, verbose_name=b'Planned Effort')),
                ('contigencyEffort', models.IntegerField(default=0, verbose_name=b'Contigency')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('projectManager', models.ForeignKey(default=None, editable=False, to=settings.AUTH_USER_MODEL, verbose_name=b'Project Manager')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectChangeInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('changedOn', models.DateField(default=None, verbose_name=b'Changed On', auto_now_add=True)),
                ('crId', models.CharField(default=None, max_length=100, verbose_name=b'Change Request ID', blank=True)),
                ('reason', models.CharField(default=None, max_length=100, verbose_name=b'Reason for change', blank=True)),
                ('endDate', models.DateField(default=None, verbose_name=b'Revised Project End Date', auto_now_add=True)),
                ('revisedEffort', models.IntegerField(default=0, verbose_name=b'Revised Effort')),
                ('closed', models.BooleanField(default=False, verbose_name=b'Close the Project')),
                ('status', models.BooleanField(default=False, verbose_name=b'Status')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('project', models.ForeignKey(verbose_name=b'Project Name', to='timesheet.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectMilestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('milestoneDate', models.DateField(default=None, verbose_name=b'Milestone Date', auto_now_add=True)),
                ('deliverables', models.CharField(default=None, max_length=100, verbose_name=b'Deliverables', blank=True)),
                ('description', models.CharField(default=None, max_length=1000, verbose_name=b'Description', blank=True)),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('project', models.ForeignKey(verbose_name=b'Project Name', to='timesheet.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectTeamMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('startDate', models.DateField(default=None, verbose_name=b'Start date on project')),
                ('plannedEffort', models.IntegerField(default=0, verbose_name=b'Planned Effort')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('member', models.ForeignKey(verbose_name=b'Team Member', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(verbose_name=b'Project Name', to='timesheet.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TimeSheetEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wkstart', models.DateField(default=None, verbose_name=b'Week Start', blank=True)),
                ('wkend', models.DateField(default=None, verbose_name=b'Week End', blank=True)),
                ('monday', models.IntegerField(default=0, verbose_name=b'Monday')),
                ('tuesday', models.IntegerField(default=0, verbose_name=b'Tuesday')),
                ('wednesday', models.IntegerField(default=0, verbose_name=b'Wednesday')),
                ('thursday', models.IntegerField(default=0, verbose_name=b'Thursday')),
                ('friday', models.IntegerField(default=0, verbose_name=b'Friday')),
                ('saturday', models.IntegerField(default=0, verbose_name=b'Saturday')),
                ('sunday', models.IntegerField(default=0, verbose_name=b'Sunday')),
                ('questionsCreated', models.IntegerField(default=0, verbose_name=b'Question Created')),
                ('approved', models.BooleanField(default=False, verbose_name=b'Approved')),
                ('approvedon', models.DateTimeField(default=None, verbose_name=b'Approved On', editable=False, blank=True)),
                ('managerFeedback', models.CharField(default=None, max_length=1000, verbose_name=b'Manager Feedback', blank=True)),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('project', models.ForeignKey(verbose_name=b'Project Name', to='timesheet.Project')),
                ('teamMember', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, verbose_name=b'Team Members')),
            ],
            options={
                'verbose_name': 'Timesheet Entry',
                'verbose_name_plural': 'Timesheet Entries',
            },
            bases=(models.Model,),
        ),
    ]
