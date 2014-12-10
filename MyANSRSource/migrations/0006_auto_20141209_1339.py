# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0005_projectteammember_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectmilestone',
            name='closed',
            field=models.BooleanField(default=False, verbose_name=b'Completed'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projectmilestone',
            name='reason',
            field=models.CharField(default=None, max_length=100, null=True, verbose_name=b'Reason for change', blank=True),
            preserve_default=True,
        ),
    ]
