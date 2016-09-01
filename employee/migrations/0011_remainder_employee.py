# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0010_remainder'),
    ]

    operations = [
        migrations.AddField(
            model_name='remainder',
            name='employee',
            field=models.ForeignKey(default=None, to='employee.Employee'),
            preserve_default=True,
        ),
    ]
