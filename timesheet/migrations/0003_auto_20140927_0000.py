# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0002_auto_20140926_2357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectchangeinfo',
            name='endDate',
            field=models.DateField(default=None, verbose_name=b'Revised Project End Date', blank=True),
        ),
        migrations.AlterField(
            model_name='projectmilestone',
            name='milestoneDate',
            field=models.DateField(default=django.utils.timezone.now, verbose_name=b'Milestone Date'),
        ),
    ]
