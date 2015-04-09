# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0063_project_salesforcenumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectchangeinfo',
            name='salesForceNumber',
            field=models.IntegerField(default=0, verbose_name=b'Sales Force                                            Oppurtunity Number', validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
    ]
