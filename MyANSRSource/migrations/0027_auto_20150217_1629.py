# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0026_auto_20150217_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='timesheetentry',
            name='task1',
            field=models.ForeignKey(verbose_name=b'Task1', to='MyANSRSource.Task', null=True),
            preserve_default=True,
        ),
    ]
