# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0107_project_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='customer',
            field=models.ForeignKey(verbose_name=b'Customer', blank=True, to='CompanyMaster.Customer', null=True),
            preserve_default=True,
        ),
    ]
