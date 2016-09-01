# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0055_sendemail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sendemail',
            name='to_addr',
        ),
        migrations.AddField(
            model_name='sendemail',
            name='toAddr',
            field=models.CharField(default=None, max_length=1000),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sendemail',
            name='content',
            field=models.CharField(default=None, max_length=1000),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sendemail',
            name='template_name',
            field=models.CharField(default=None, max_length=100),
            preserve_default=True,
        ),
    ]
