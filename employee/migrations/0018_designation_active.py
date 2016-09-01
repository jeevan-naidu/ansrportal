# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0017_employee_uan'),
    ]

    operations = [
        migrations.AddField(
            model_name='designation',
            name='active',
            field=models.BooleanField(default=True, verbose_name=b'Is Active?'),
            preserve_default=True,
        ),
    ]
