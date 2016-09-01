# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0063_auto_20150402_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.IntegerField(default=None, null=True, verbose_name=b'ISBN', blank=True),
            preserve_default=True,
        ),
    ]
