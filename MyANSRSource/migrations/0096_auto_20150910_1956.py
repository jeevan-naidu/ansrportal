# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0095_auto_20150830_0907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='taskType',
            field=models.CharField(default=None, max_length=2, verbose_name=b'Task type', choices=[(b'B', b'Revenue'), (b'I', b'Idle'), (b'N', b'Non-Revenue')]),
            preserve_default=True,
        ),
    ]
