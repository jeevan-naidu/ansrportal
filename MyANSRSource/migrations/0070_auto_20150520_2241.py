# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0069_auto_20150423_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='projectId',
            field=models.CharField(unique=True, max_length=60, verbose_name=b'Project Code'),
            preserve_default=True,
        ),
    ]
