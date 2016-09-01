# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0088_activity_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='active',
            field=models.BooleanField(default=True, verbose_name=b'Is Active?'),
            preserve_default=True,
        ),
    ]
