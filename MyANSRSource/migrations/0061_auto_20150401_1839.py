# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0060_projectmilestone_closedon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectchangeinfo',
            name='closedOn',
            field=models.DateTimeField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
    ]
