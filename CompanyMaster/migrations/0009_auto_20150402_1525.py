# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0008_auto_20150221_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='training',
            name='endDate',
            field=models.DateField(default=None, verbose_name=b'End Date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='training',
            name='trainingDate',
            field=models.DateField(default=None, verbose_name=b'Start Date'),
            preserve_default=True,
        ),
    ]
