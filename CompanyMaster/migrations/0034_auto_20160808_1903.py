# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0033_auto_20160808_1901'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customernew',
            name='HQ_address',
        ),
        migrations.RemoveField(
            model_name='customernew',
            name='account_delivery_manager',
        ),
        migrations.RemoveField(
            model_name='customernew',
            name='account_relationship_manager',
        ),
        migrations.RemoveField(
            model_name='customernew',
            name='bill_to_address',
        ),
        migrations.RemoveField(
            model_name='customernew',
            name='business_segment',
        ),
        migrations.RemoveField(
            model_name='customernew',
            name='customer_type',
        ),
        migrations.RemoveField(
            model_name='customernew',
            name='group_customer_name',
        ),
        migrations.RemoveField(
            model_name='customernew',
            name='ship_to_address',
        ),
        migrations.DeleteModel(
            name='CustomerNew',
        ),
    ]
