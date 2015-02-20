# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0027_auto_20150217_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='taskType',
            field=models.CharField(default=None, max_length=2, verbose_name=b'Task type', choices=[(b'B', b'Billable'), (b'I', b'Idle')]),
            preserve_default=True,
        ),
    ]
