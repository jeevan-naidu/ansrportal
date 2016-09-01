# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0068_report'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='contingencyEffort',
            field=models.IntegerField(default=0, null=True, verbose_name=b'Contigency Effort', blank=True, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
    ]
