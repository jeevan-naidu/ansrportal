# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0018_auto_20141218_1207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='projectId',
            field=models.CharField(max_length=60),
            preserve_default=True,
        ),
    ]
