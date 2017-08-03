# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0082_auto_20150720_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='btgreport',
            name='currMonthIN',
            field=models.IntegerField(default=0, verbose_name=b'Number Of Invoices', validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
    ]
