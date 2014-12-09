# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0004_auto_20141209_1005'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectteammember',
            name='rate',
            field=models.IntegerField(default=0, verbose_name=b'%'),
            preserve_default=True,
        ),
    ]
