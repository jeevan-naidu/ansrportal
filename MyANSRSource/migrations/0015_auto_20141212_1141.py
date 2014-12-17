# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0014_auto_20141211_1845'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectchangeinfo',
            name='status',
        ),
        migrations.AddField(
            model_name='projectchangeinfo',
            name='closedOn',
            field=models.DateField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectchangeinfo',
            name='revisedTotal',
            field=models.IntegerField(default=0, verbose_name=b'Revised amount'),
            preserve_default=True,
        ),
    ]
