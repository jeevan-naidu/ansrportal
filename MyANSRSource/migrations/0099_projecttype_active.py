# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0098_auto_20150923_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='projecttype',
            name='active',
            field=models.BooleanField(default=True, verbose_name=b'Is Active?'),
            preserve_default=True,
        ),
    ]
