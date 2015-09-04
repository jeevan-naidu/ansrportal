# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0008_auto_20150902_1424'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emppeer',
            name='employee',
        ),
    ]
