# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0067_project_customercontact'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'permissions': (('create_project', 'Create ANSR projects'), ('manage_project', 'Manage ANSR Project'), ('approve_timesheet', 'Approve timesheets'), ('manage_milestones', 'Manage Project Milestones'), ('view_all_projects', 'View all projects'))},
        ),
        migrations.AlterField(
            model_name='project',
            name='salesForceNumber',
            field=models.IntegerField(default=0, verbose_name=b'SF                                           Oppurtunity Number', validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
    ]
