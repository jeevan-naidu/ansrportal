# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0045_auto_20150225_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='po',
            field=models.CharField(default=0, max_length=60, verbose_name=b'P.O.'),
            preserve_default=True,
        ),
    ]
