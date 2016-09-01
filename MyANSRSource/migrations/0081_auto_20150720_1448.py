# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0080_auto_20150720_1446'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='btgreport',
            name='currMonthAE',
        ),
        migrations.RemoveField(
            model_name='btgreport',
            name='lastMonthAE',
        ),
    ]
