# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0013_auto_20141211_1713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectmilestone',
            name='description',
            field=models.CharField(default=None, max_length=1000, null=True, verbose_name=b'Description'),
            preserve_default=True,
        ),
    ]
