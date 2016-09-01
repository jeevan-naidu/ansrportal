# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0043_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='po',
            field=models.CharField(default=None, max_length=60, null=True, verbose_name=b'P.O.', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='activity',
            field=models.ForeignKey(verbose_name=b'Activity', to='MyANSRSource.Activity', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='task',
            field=models.ForeignKey(verbose_name=b'Task', to='MyANSRSource.Task', null=True),
            preserve_default=True,
        ),
    ]
