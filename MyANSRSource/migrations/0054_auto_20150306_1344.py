# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0053_auto_20150305_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='taskType',
            field=models.CharField(default=None, max_length=2, verbose_name=b'Task type', choices=[(b'B', b'Billable'), (b'I', b'Non Billable')]),
            preserve_default=True,
        ),
    ]
