# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0009_auto_20150122_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projecttype',
            name='code',
            field=models.CharField(max_length=2, verbose_name=b'Unit of Work'),
            preserve_default=True,
        ),
    ]
