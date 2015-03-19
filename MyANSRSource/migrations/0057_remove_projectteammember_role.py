# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0056_auto_20150316_1244'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectteammember',
            name='role',
        ),
    ]
