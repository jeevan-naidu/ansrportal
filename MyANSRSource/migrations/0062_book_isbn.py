# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0061_auto_20150401_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='isbn',
            field=models.IntegerField(default=0, verbose_name=b'ISBN'),
            preserve_default=True,
        ),
    ]
