# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0015_auto_20150609_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='bank_account',
            field=models.IntegerField(max_length=30, unique=True, null=True, verbose_name=b'Account Number', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='employee',
            name='bank_branch',
            field=models.CharField(max_length=70, null=True, verbose_name=b'Branch Name', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='employee',
            name='bank_ifsc_code',
            field=models.CharField(max_length=20, null=True, verbose_name=b'IFSC Code', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='employee',
            name='bank_name',
            field=models.CharField(max_length=70, null=True, verbose_name=b'Bank Name', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='employee',
            name='date_of_birthO',
            field=models.DateField(default=None, verbose_name=b'Official DOB'),
            preserve_default=True,
        ),
    ]
