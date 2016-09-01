# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0036_customer'),
        ('MyANSRSource', '0109_remove_project_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='customer',
            field=models.ForeignKey(verbose_name=b'Customer', blank=True, to='CompanyMaster.Customer', null=True),
            preserve_default=True,
        ),
    ]
