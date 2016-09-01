# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0085_projectteammember_datapoint'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='maxProductivityUnits',
        ),
    ]
