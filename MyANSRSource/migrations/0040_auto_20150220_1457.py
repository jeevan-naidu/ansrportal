# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0039_auto_20150220_1207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='endDate',
            field=models.DateField(default=django.utils.timezone.now, verbose_name=b'Project End Date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='startDate',
            field=models.DateField(default=django.utils.timezone.now, verbose_name=b'Project Start Date'),
            preserve_default=True,
        ),
    ]
