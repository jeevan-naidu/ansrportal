# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0016_auto_20150209_1229'),
    ]

    operations = [
        migrations.AddField(
            model_name='timesheetentry',
            name='toApprove',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
