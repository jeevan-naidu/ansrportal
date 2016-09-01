# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0014_auto_20150608_1103'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='date_of_birth',
            new_name='date_of_birthO',
        ),
        migrations.AddField(
            model_name='employee',
            name='date_of_birthR',
            field=models.DateField(default=None, verbose_name=b'Alternate DOB'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='remainder',
            name='endDate',
            field=models.DateField(default=django.utils.timezone.now,
                                   verbose_name=b'End Date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='remainder',
            name='startDate',
            field=models.DateField(default=django.utils.timezone.now,
                                   verbose_name=b'Start Date'),
            preserve_default=True,
        ),
    ]
