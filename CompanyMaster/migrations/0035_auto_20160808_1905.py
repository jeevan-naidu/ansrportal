# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0106_remove_project_customer'),
        ('CompanyMaster', '0034_auto_20160808_1903'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='CType',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='Cdelivery',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='Crelation',
        ),
        migrations.DeleteModel(
            name='Customer',
        ),
    ]
