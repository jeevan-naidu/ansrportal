# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0017_auto_20141212_1237'),
    ]

    operations = [
        migrations.AddField(
            model_name='timesheetentry',
            name='sundayH',
            field=models.IntegerField(default=0, verbose_name=b'Sun'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='timesheetentry',
            name='sundayQ',
            field=models.IntegerField(default=0, verbose_name=b'Sun'),
            preserve_default=True,
        ),
    ]
