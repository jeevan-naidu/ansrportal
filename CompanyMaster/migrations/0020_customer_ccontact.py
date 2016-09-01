# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0019_auto_20150731_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='cContact',
            field=models.CharField(default=None, max_length=100, verbose_name=b'Customer contact'),
            preserve_default=True,
        ),
    ]
