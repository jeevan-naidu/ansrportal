# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0074_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'permissions': (('create_project', 'Create ANSR projects'), ('manage_project', 'Manage ANSR Project'), ('approve_timesheet', 'Approve timesheets'), ('manage_milestones', 'Manage Project Milestones'), ('view_all_projects', 'View all projects'), ('report_project', 'Project Level Report'), ('report_bu', 'BU Level Report'), ('report_superuser', 'SuperUser Level Report'))},
        ),
    ]
