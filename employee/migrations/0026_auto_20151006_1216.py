# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0025_auto_20150831_1559'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='is_360eligible',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='reportees',
        ),
    ]
