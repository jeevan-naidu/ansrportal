# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0015_auto_20150910_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='category',
            field=models.ManyToManyField(default=None, to='employee.Designation'),
            preserve_default=True,
        ),
    ]
