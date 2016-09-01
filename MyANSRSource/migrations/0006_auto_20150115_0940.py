# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0005_auto_20150114_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectchangeinfo',
            name='endDate',
            field=models.DateField(default=None, verbose_name=b'Revised Project End Date'),
            preserve_default=True,
        ),
    ]
