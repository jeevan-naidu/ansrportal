# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0093_auto_20150830_0846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='name',
            field=models.CharField(default=b'nonclosedprojectts', max_length=50, verbose_name=b'Report', choices=[(b'nonclosedprojectts', b'Non Closed Project TS')]),
            preserve_default=True,
        ),
    ]
