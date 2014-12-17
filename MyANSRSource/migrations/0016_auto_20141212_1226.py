# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0015_auto_20141212_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='timesheetentry',
            name='hold',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='approved',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
