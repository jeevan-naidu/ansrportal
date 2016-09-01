# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0113_auto_20160808_1932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='customer',
            field=models.ForeignKey(default=None, verbose_name=b'Customer', to='CompanyMaster.Customer'),
            preserve_default=True,
        ),
    ]
