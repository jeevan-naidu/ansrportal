# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0025_auto_20150217_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='timesheetentry',
            name='activity1',
            field=models.ForeignKey(verbose_name=b'Activity1', to='MyANSRSource.Activity', null=True),
            preserve_default=True,
        ),
    ]
