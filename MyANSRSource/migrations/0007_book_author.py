# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0006_auto_20150115_0940'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='author',
            field=models.CharField(default='--To be Provided--', max_length=100, verbose_name=b'Author'),
            preserve_default=False,
        ),
    ]
