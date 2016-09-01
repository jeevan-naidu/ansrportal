# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0079_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='btgreport',
            name='btgDate',
        ),
        migrations.AddField(
            model_name='btgreport',
            name='btgMonth',
            field=models.IntegerField(default=1, verbose_name=b'BTG', validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='btgreport',
            name='btgYear',
            field=models.IntegerField(default=1990, verbose_name=b'BTG', validators=[django.core.validators.MinValueValidator(1990)]),
            preserve_default=True,
        ),
    ]
