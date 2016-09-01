# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0022_auto_20150731_1641'),
        ('MyANSRSource', '0084_auto_20150727_1909'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectteammember',
            name='datapoint',
            field=models.ForeignKey(blank=True, to='CompanyMaster.DataPoint', null=True),
            preserve_default=True,
        ),
    ]
