# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0030_auto_20150218_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='po',
            field=models.CharField(default=None, max_length=60, verbose_name=b'P.O.'),
            preserve_default=True,
        ),
    ]
