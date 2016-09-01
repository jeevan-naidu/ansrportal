# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0031_question_qtype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='priority',
            field=models.IntegerField(max_length=100, verbose_name=b'Priority', validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
    ]
