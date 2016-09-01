# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0062_book_isbn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.IntegerField(default=0, null=True, verbose_name=b'ISBN', blank=True),
            preserve_default=True,
        ),
    ]
