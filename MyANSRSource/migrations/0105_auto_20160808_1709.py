# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0104_auto_20160518_2003'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='norm',
        ),
        migrations.AddField(
            model_name='task',
            name='measure_productivity',
            field=models.CharField(default='yes', max_length=200, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='task',
            name='code',
            field=models.CharField(default=None, max_length=20, verbose_name=b'Short Code'),
            preserve_default=True,
        ),
    ]
