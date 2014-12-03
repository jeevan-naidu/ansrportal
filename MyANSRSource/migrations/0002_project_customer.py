# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0003_customer'),
        ('MyANSRSource', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='customer',
            field=models.ForeignKey(default=None, verbose_name=b'Customer', to='CompanyMaster.Customer'),
            preserve_default=True,
        ),
    ]
