# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0010_auto_20150201_1052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='name',
            field=models.CharField(max_length=100, verbose_name=b'Name'),
            preserve_default=True,
        ),
    ]
