# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='ans',
            field=models.CharField(max_length=100, verbose_name=b'Choice'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='question',
            name='ans',
            field=models.ManyToManyField(default=None, to='fb360.Answer', verbose_name=b'Choice'),
            preserve_default=True,
        ),
    ]
