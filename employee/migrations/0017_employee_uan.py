# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0016_auto_20150609_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='uan',
            field=models.IntegerField(max_length=12, unique=True, null=True, verbose_name=b'Universal account number', blank=True),
            preserve_default=True,
        ),
    ]
