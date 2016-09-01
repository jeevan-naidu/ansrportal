# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0018_auto_20150210_1103'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'permissions': (('create_project', 'Create ANSR projects'), ('manage_project', 'Manage ANSR Project'), ('approve_timesheet', 'Approve timesheets'), ('manage_milestones', 'Manage Project Milestones'))},
        ),
    ]
