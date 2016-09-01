# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0013_auto_20150413_1443'),
    ]

    operations = [
        migrations.RenameField(
            model_name='remainder',
            old_name='date',
            new_name='endDate',
        ),
        migrations.AddField(
            model_name='remainder',
            name='startDate',
            field=models.DateField(default=django.utils.timezone.now, verbose_name=b'Date'),
            preserve_default=True,
        ),
    ]
