# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0041_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timesheetentry',
            name='activity',
        ),
        migrations.RemoveField(
            model_name='timesheetentry',
            name='task',
        ),
        migrations.RenameField(
            model_name='timesheetentry',
            old_name='activity1',
            new_name='activity',
        ),
        migrations.RenameField(
            model_name='timesheetentry',
            old_name='task1',
            new_name='task',
        ),
    ]
