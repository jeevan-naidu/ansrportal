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
                ('name', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectChangeInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('changed_on', models.DateField(auto_now_add=True)),
                ('cr_id', models.CharField(default=None, max_length=100, blank=True)),
                ('reason', models.CharField(max_length=100)),
                ('end_date', models.DateField(auto_now_add=True, verbose_name=b'Revised Project End Date', null=True)),
                ('revised_effort', models.IntegerField(default=0)),
                ('approved', models.BooleanField(default=False)),
                ('project', models.ForeignKey(to='timesheet.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectMilestones',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('milestone_date', models.DateField(default=None, verbose_name=b'Milestone Date', auto_now_add=True)),
                ('description', models.CharField(default=None, max_length=100, blank=True)),
                ('project', models.ForeignKey(to='timesheet.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectTeam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('member', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(to='timesheet.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TSEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wkstart', models.DateField(auto_now_add=True, verbose_name=b'Week Start')),
                ('wkend', models.DateField(auto_now_add=True, verbose_name=b'Week Ending')),
                ('monday', models.IntegerField(default=0)),
                ('approved', models.BooleanField(default=False)),
                ('project', models.ForeignKey(to='timesheet.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
