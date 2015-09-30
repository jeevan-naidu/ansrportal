# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0035_auto_20150930_1926'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='priority',
            field=models.IntegerField(default=None, max_length=100, verbose_name=b'Priority', validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
    ]
