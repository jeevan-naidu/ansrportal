# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SalesforceData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('opportunity_number', models.IntegerField(default=0, help_text=b'8 digit number starting with 201', unique=True, verbose_name=b'SF                                           Oppurtunity Number', validators=[django.core.validators.MinValueValidator(20100000), django.core.validators.MaxValueValidator(99999999)])),
                ('opportunity_name', models.CharField(max_length=300)),
                ('business_unit', models.CharField(max_length=100)),
                ('customer_contact', models.CharField(max_length=100, verbose_name=b'Customer Contact')),
                ('account_name', models.CharField(max_length=100, null=True, blank=True)),
                ('value', models.DecimalField(verbose_name=b'Project Value(in $)', max_digits=20, decimal_places=5)),
                ('probability', models.IntegerField()),
                ('start_date', models.DateField(null=True, verbose_name=b'Estimated End Date', blank=True)),
                ('end_date', models.DateField(null=True, verbose_name=b'Estimated Start Date', blank=True)),
                ('status', models.CharField(max_length=100, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
