# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0069_auto_20150423_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheetentry',
            name='mondayH',
            field=models.DecimalField(default=0.0, verbose_name=b'Mon', max_digits=12, decimal_places=2, validators=[django.core.validators.MinLengthValidator(4)]),
            preserve_default=True,
        ),
    ]
