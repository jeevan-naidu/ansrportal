# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0006_auto_20150227_1559'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='swipe_location',
        ),
    ]
