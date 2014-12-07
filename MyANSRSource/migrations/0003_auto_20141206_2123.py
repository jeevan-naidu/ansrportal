# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0002_auto_20141206_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectchangeinfo',
            name='crId',
            field=models.CharField(default=None, max_length=100, null=True, verbose_name=b'Change Request ID', blank=True),
            preserve_default=True,
        ),
    ]
