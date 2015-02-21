# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0028_task_tasktype'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='po',
            field=models.CharField(default=None, max_length=60, blank=True),
            preserve_default=True,
        ),
    ]
