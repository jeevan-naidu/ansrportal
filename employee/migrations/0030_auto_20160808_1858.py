# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0029_employee_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='company',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='location',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='pratice',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='sub_practice',
        ),
    ]
