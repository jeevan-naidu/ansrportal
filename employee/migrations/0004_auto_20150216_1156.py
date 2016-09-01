# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0003_remove_employee_division'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empaddress',
            name='address1',
            field=models.CharField(max_length=100, verbose_name=b'Address 1'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='empaddress',
            name='address2',
            field=models.CharField(max_length=100, verbose_name=b'Address 2'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='empaddress',
            name='city',
            field=models.CharField(max_length=30, verbose_name=b'City'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='empaddress',
            name='state',
            field=models.CharField(max_length=30, verbose_name=b'State'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='empaddress',
            name='zipcode',
            field=models.CharField(max_length=10, verbose_name=b'Zip Code'),
            preserve_default=True,
        ),
    ]
