# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0002_auto_20150109_1656'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='timesheetentry',
            options={'verbose_name': 'Timesheet Entry', 'verbose_name_plural': 'Timesheet Entries', 'permissions': (('enter_timesheet', 'Allow timetracking'),)},
        ),
    ]
