# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-02 10:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QMS', '0004_auto_20161102_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewreport',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Is Fixed?'),
        ),
    ]
