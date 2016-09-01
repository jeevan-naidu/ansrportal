# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0019_remove_timesheetentry_toapprove'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectteammember',
            name='endDate',
            field=models.DateField(default=django.utils.timezone.now, verbose_name=b'End date on project', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectteammember',
            name='member',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectteammember',
            name='plannedEffort',
            field=models.IntegerField(default=0, verbose_name=b'Planned Effort', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectteammember',
            name='rate',
            field=models.IntegerField(default=100, verbose_name=b'%', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectteammember',
            name='role',
            field=models.ForeignKey(default=None, blank=True, to='employee.Designation', null=True, verbose_name=b'Role'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectteammember',
            name='startDate',
            field=models.DateField(default=django.utils.timezone.now, verbose_name=b'Start date on project', blank=True),
            preserve_default=True,
        ),
    ]
