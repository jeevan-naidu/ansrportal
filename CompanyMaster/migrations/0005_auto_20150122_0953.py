# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0004_auto_20150119_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='customerCode',
            field=models.CharField(default=None, max_length=3, verbose_name=b'Customer Code'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customer',
            name='seqNumber',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
