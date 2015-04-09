# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0013_customer_internal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='internal',
            field=models.BooleanField(default=False, verbose_name=b'Internal Customer'),
            preserve_default=True,
        ),
    ]
