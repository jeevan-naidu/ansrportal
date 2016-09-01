# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0032_auto_20150218_1840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='code',
            field=models.CharField(default=None, unique=True, max_length=1, verbose_name=b'Short Code'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='code',
            field=models.CharField(default=None, unique=True, max_length=1, verbose_name=b'Short Code'),
            preserve_default=True,
        ),
    ]
