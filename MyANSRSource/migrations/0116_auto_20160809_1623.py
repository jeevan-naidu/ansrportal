# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0115_auto_20160808_1935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projecttype',
            name='code',
            field=models.CharField(help_text=b'max length 10', max_length=10, verbose_name=b'Unit of Work'),
            preserve_default=True,
        ),
    ]
