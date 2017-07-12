# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0048_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='po',
            field=models.CharField(default=0, max_length=60, verbose_name=b'P.O.', validators=[django.core.validators.RegexValidator(b'^[0-9a-zA-Z]*$', b'Only alphanumeric characters are allowed.')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectchangeinfo',
            name='revisedEffort',
            field=models.IntegerField(default=0, verbose_name=b'Revised Effort', validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectchangeinfo',
            name='revisedTotal',
            field=models.DecimalField(default=0.0, verbose_name=b'Revised amount', max_digits=12, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
    ]
