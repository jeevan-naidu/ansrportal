# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0103_auto_20151217_1636'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='customerContact',
            field=models.CharField(default=None, max_length=100, verbose_name=b'Customer Contact'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='salesForceNumber',
            field=models.IntegerField(default=0, help_text=b'8 digit number starting with 201', verbose_name=b'SF                                           Oppurtunity Number', validators=[django.core.validators.MinValueValidator(20100000), django.core.validators.MaxValueValidator(99999999)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectchangeinfo',
            name='salesForceNumber',
            field=models.IntegerField(default=0, help_text=b'8 digit number starting with 201', verbose_name=b'Sales Force                                            Oppurtunity Number', validators=[django.core.validators.MinValueValidator(20100000), django.core.validators.MaxValueValidator(99999999)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectteammember',
            name='datapoint',
            field=models.ForeignKey(verbose_name='Service Line', blank=True, to='CompanyMaster.DataPoint', null=True),
            preserve_default=True,
        ),
    ]
