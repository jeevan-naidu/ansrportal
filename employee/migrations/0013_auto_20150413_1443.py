# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0012_remove_remainder_color'),
    ]

    operations = [
        migrations.RenameField(
            model_name='remainder',
            old_name='employee',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='remainder',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name=b'Date'),
            preserve_default=True,
        ),
    ]
