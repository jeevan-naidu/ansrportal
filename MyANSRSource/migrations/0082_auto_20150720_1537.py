# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0081_auto_20150720_1448'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='btgreport',
            name='lastMonthIN',
        ),
        migrations.RemoveField(
            model_name='btgreport',
            name='lastMonthRR',
        ),
    ]
