# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0096_auto_20150910_1956'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectteammember',
            name='active',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
