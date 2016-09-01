# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0071_auto_20150525_1239'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='norm',
            field=models.DecimalField(default=0.0, verbose_name=b'Norm', max_digits=12, decimal_places=2, validators=[django.core.validators.MinValueValidator(0.0)]),
            preserve_default=True,
        ),
    ]
