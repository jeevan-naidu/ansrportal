# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0005_auto_20141203_2241'),
    ]

    operations = [
        migrations.AddField(
            model_name='designation',
            name='billable',
            field=models.BooleanField(default=True, verbose_name=b'Billable ?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='designation',
            name='name',
            field=models.CharField(max_length=40, verbose_name=b'Title'),
            preserve_default=True,
        ),
    ]
