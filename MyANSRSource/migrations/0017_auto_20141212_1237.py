# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0016_auto_20141212_1226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheetentry',
            name='approved',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
