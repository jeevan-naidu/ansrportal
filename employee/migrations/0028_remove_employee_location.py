# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0027_auto_20160808_1724'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='location',
        ),
    ]
