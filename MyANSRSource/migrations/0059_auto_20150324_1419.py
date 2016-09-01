# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0058_auto_20150324_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectchangeinfo',
            name='reason',
            field=models.CharField(default=None, max_length=100, verbose_name=b'Reason for change'),
            preserve_default=True,
        ),
    ]
