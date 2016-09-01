# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0036_auto_20150219_2344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='contingencyEffort',
            field=models.IntegerField(default=0, verbose_name=b'Contigency Effort', validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='maxProductivityUnits',
            field=models.DecimalField(default=0.0, verbose_name=b'Norm', max_digits=12, decimal_places=2, validators=[django.core.validators.MinValueValidator(0.0)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='plannedEffort',
            field=models.IntegerField(default=0, verbose_name=b'Planned Effort', validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='totalValue',
            field=models.DecimalField(default=0.0, verbose_name=b'Total Value', max_digits=12, decimal_places=2, validators=[django.core.validators.MinValueValidator(0.0)]),
            preserve_default=True,
        ),
    ]
