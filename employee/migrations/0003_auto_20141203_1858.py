# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0002_auto_20141203_1825'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='previous_employment',
        ),
        migrations.AddField(
            model_name='previousemployment',
            name='employee',
            field=models.ForeignKey(default=1, to='employee.Employee'),
            preserve_default=False,
        ),
    ]
