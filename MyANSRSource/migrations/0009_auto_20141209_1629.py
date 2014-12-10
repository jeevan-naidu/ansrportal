# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0008_auto_20141209_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='internal',
            field=models.BooleanField(default=None, verbose_name=b'Internal Project'),
            preserve_default=True,
        ),
    ]
