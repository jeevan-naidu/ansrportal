# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-12-06 08:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('QMS', '0019_auto_20161205_1203'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalqasheetheader',
            old_name='order',
            new_name='order_number',
        ),
        migrations.RenameField(
            model_name='qasheetheader',
            old_name='order',
            new_name='order_number',
        ),
    ]
