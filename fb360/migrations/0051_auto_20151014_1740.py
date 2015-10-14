# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0050_auto_20151008_1215'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('category__name',)},
        ),
        migrations.AlterField(
            model_name='question',
            name='category',
            field=models.ManyToManyField(default=None, to='employee.Designation', verbose_name=b'Roles'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='question',
            name='qst',
            field=models.CharField(max_length=256, verbose_name=b'Question'),
            preserve_default=True,
        ),
    ]
