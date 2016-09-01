# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0002_holiday_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='holiday',
            name='location',
        ),
        migrations.AddField(
            model_name='holiday',
            name='location1',
            field=models.ManyToManyField(default=None, to='CompanyMaster.OfficeLocation'),
            preserve_default=True,
        ),
    ]
