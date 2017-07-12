# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-07-11 11:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Invoice', '0002_auto_20170711_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='payment_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='payment_status',
            field=models.CharField(choices=[(b'yes', b'Approve'), (b'no', b'Reject')], default=1, max_length=10),
            preserve_default=False,
        ),
    ]
