# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0105_auto_20160808_1709'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='customer',
        ),
    ]
