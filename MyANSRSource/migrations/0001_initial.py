# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('CompanyMaster', '0001_initial'),
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Book Name')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Chapter Name')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('book', models.ForeignKey(to='MyANSRSource.Book')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Location Name')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('projectType', models.CharField(default=b'Q', max_length=2, verbose_name=b'Project Type', choices=[(b'Q', b'Questions'), (b'P', b'Powerpoint'), (b'I', b'Instructional')])),
                ('name', models.CharField(max_length=50, verbose_name=b'Project Name')),
                ('currentProject', models.BooleanField(default=True, verbose_name=b'Project Stage')),
                ('signed', models.BooleanField(default=True, verbose_name=b'Contact Signed')),
                ('internal', models.BooleanField(default=True, verbose_name=b'Internal Project')),
                ('projectId', models.CharField(max_length=15)),
                ('startDate', models.DateTimeField(verbose_name=b'Project Start Date')),
                ('endDate', models.DateTimeField(verbose_name=b'Project End Date')),
                ('plannedEffort', models.IntegerField(default=0, verbose_name=b'Planned Effort')),
                ('contingencyEffort', models.IntegerField(default=0, verbose_name=b'Contigency Effort')),
                ('totalValue', models.IntegerField(default=0, verbose_name=b'Total Value')),
                ('closed', models.BooleanField(default=False, verbose_name=b'Project Closed')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('book', models.ForeignKey(default=None, verbose_name=b'Book', to='MyANSRSource.Book')),
                ('bu', models.ForeignKey(verbose_name=b'Business Unit', to='CompanyMaster.BusinessUnit')),
                ('chapters', models.ManyToManyField(to='MyANSRSource.Chapter')),
                ('customer', models.ForeignKey(default=None, verbose_name=b'Customer', to='CompanyMaster.Customer')),
                ('projectManager', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectChangeInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('crId', models.CharField(default=None, max_length=100, verbose_name=b'Change Request ID', blank=True)),
                ('reason', models.CharField(default=None, max_length=100, verbose_name=b'Reason for change', blank=True)),
                ('endDate', models.DateField(default=None, verbose_name=b'Revised Project End Date', blank=True)),
                ('revisedEffort', models.IntegerField(default=0, verbose_name=b'Revised Effort')),
                ('revisedTotal', models.IntegerField(default=0, verbose_name=b'Revised Total')),
                ('closed', models.BooleanField(default=False, verbose_name=b'Close the Project')),
                ('signed', models.BooleanField(default=False, verbose_name=b'Contract Signed')),
                ('status', models.BooleanField(default=False, verbose_name=b'Status')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectMilestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('milestoneDate', models.DateField(default=django.utils.timezone.now, verbose_name=b'Milestone Date')),
                ('deliverables', models.CharField(default=None, max_length=100, verbose_name=b'Deliverables', blank=True)),
                ('description', models.CharField(default=None, max_length=1000, verbose_name=b'Description', blank=True)),
                ('amount', models.IntegerField(default=0, verbose_name=b'Amount')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('project', models.ForeignKey(to='MyANSRSource.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectTeamMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('startDate', models.DateField(default=django.utils.timezone.now, verbose_name=b'Start date on project')),
                ('endDate', models.DateField(default=django.utils.timezone.now, verbose_name=b'End date on project')),
                ('plannedEffort', models.IntegerField(default=0, verbose_name=b'Planned Effort')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('member', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(to='MyANSRSource.Project')),
                ('role', models.ForeignKey(default=None, verbose_name=b'Role', to='employee.Designation')),
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
                ('activity', models.CharField(max_length=2, null=True)),
                ('task', models.CharField(max_length=2, null=True)),
                ('mondayQ', models.IntegerField(default=0, verbose_name=b'Mon')),
                ('mondayH', models.IntegerField(default=0, verbose_name=b'Mon')),
                ('tuesdayQ', models.IntegerField(default=0, verbose_name=b'Tue')),
                ('tuesdayH', models.IntegerField(default=0, verbose_name=b'Tue')),
                ('wednesdayQ', models.IntegerField(default=0, verbose_name=b'Wed')),
                ('wednesdayH', models.IntegerField(default=0, verbose_name=b'Wed')),
                ('thursdayQ', models.IntegerField(default=0, verbose_name=b'Thu')),
                ('thursdayH', models.IntegerField(default=0, verbose_name=b'Thu')),
                ('fridayQ', models.IntegerField(default=0, verbose_name=b'Fri')),
                ('fridayH', models.IntegerField(default=0, verbose_name=b'Fri')),
                ('saturdayQ', models.IntegerField(default=0, verbose_name=b'Sat')),
                ('saturdayH', models.IntegerField(default=0, verbose_name=b'Sat')),
                ('totalQ', models.IntegerField(default=0, verbose_name=b'Total')),
                ('totalH', models.IntegerField(default=0, verbose_name=b'Total')),
                ('approved', models.BooleanField(default=False, verbose_name=b'Approved')),
                ('approvedon', models.DateTimeField(default=None, verbose_name=b'Approved On', null=True, editable=False, blank=True)),
                ('managerFeedback', models.CharField(default=None, max_length=1000, null=True, verbose_name=b'Manager Feedback', blank=True)),
                ('exception', models.CharField(default=b'No Exception', max_length=75)),
                ('billable', models.BooleanField(default=False, verbose_name=b'Billable')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('chapter', models.ForeignKey(verbose_name=b'Chapter', to='MyANSRSource.Chapter', null=True)),
                ('location', models.ForeignKey(verbose_name=b'Location', to='MyANSRSource.Location', null=True)),
                ('project', models.ForeignKey(verbose_name=b'Project Name', to='MyANSRSource.Project', null=True)),
                ('teamMember', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Timesheet Entry',
                'verbose_name_plural': 'Timesheet Entries',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='projectchangeinfo',
            name='milestone',
            field=models.ForeignKey(to='MyANSRSource.ProjectMilestone'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projectchangeinfo',
            name='project',
            field=models.ForeignKey(verbose_name=b'Project Name', to='MyANSRSource.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projectchangeinfo',
            name='teamMember',
            field=models.ForeignKey(to='MyANSRSource.ProjectTeamMember'),
            preserve_default=True,
        ),
    ]
