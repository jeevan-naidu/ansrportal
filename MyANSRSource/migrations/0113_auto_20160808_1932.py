# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0112_auto_20160808_1928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='customer',
            field=models.ForeignKey(verbose_name=b'Customer', blank=True, to='CompanyMaster.Customer', null=True),
            preserve_default=True,
        ),
    ]
