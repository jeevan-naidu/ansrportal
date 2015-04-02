# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0009_auto_20150402_1525'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='location',
            field=models.CharField(default=None, max_length=100, verbose_name=b'Location'),
            preserve_default=True,
        ),
    ]
