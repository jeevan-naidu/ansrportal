# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0025_auto_20150831_1559'),
        ('fb360', '0038_remove_fb360_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='fb360',
            name='eligible',
            field=models.ManyToManyField(default=None, to='employee.Employee'),
            preserve_default=True,
        ),
    ]
