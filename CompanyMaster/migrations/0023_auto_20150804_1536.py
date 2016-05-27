# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0022_auto_20150731_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='active',
            field=models.BooleanField(default=True, verbose_name=b'Is Active?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customer',
            name='address',
            field=models.CharField(default=None, max_length=100, verbose_name=b'Address'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='officelocation',
            name='active',
            field=models.BooleanField(default=True, verbose_name=b'Is Active?'),
            preserve_default=True,
        ),
    ]
