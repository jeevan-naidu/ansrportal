# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0023_activity_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='code',
            field=models.CharField(default=None, max_length=1, verbose_name=b'Short Code'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='code',
            field=models.CharField(default=None, max_length=1, verbose_name=b'Short Code'),
            preserve_default=True,
        ),
    ]
