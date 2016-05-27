# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0019_employee_manager'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='is_360eligible',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
