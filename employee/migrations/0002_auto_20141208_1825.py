# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='education',
            name='institute',
            field=models.CharField(max_length=50, verbose_name=b'Institution'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='education',
            name='name',
            field=models.CharField(max_length=50, verbose_name=b'Qualification'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='employee',
            name='PF_number',
            field=models.CharField(max_length=14, verbose_name=b'Provident Fund Number', blank=True),
            preserve_default=True,
        ),
    ]
