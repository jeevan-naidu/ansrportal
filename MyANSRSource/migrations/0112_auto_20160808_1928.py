# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0036_customer'),
        ('MyANSRSource', '0111_remove_project_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='customer',
            field=models.ForeignKey(default=None, verbose_name=b'Customer', to='CompanyMaster.Customer'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='norm',
            field=models.DecimalField(default=0.0, verbose_name=b'Norm', max_digits=12, decimal_places=2, validators=[django.core.validators.MinValueValidator(0.0)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='code',
            field=models.CharField(default=None, max_length=1, verbose_name=b'Short Code'),
            preserve_default=True,
        ),
    ]
