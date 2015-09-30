# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0025_auto_20150831_1559'),
        ('fb360', '0034_group_fb'),
    ]

    operations = [
        migrations.AddField(
            model_name='fb360',
            name='category',
            field=models.ManyToManyField(default=None, to='employee.Employee'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fb360',
            name='name',
            field=models.CharField(default=None, max_length=100, verbose_name=b'Name'),
            preserve_default=True,
        ),
    ]
