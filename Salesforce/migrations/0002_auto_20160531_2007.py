# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('Salesforce', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='salesforcedata',
            options={'verbose_name_plural': 'Salesforce Data'},
        ),
        migrations.AddField(
            model_name='salesforcedata',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 5, 31, 20, 6, 26, 376369), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='salesforcedata',
            name='updated_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 5, 31, 20, 6, 37, 758463), verbose_name=b'Updated Date', auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='salesforcedata',
            name='account_name',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='salesforcedata',
            name='business_unit',
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='salesforcedata',
            name='customer_contact',
            field=models.CharField(max_length=100, null=True, verbose_name=b'Customer Contact', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='salesforcedata',
            name='end_date',
            field=models.DateField(default=datetime.datetime(2016, 5, 31, 20, 7, 2, 456497), verbose_name=b'Estimated End Date'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='salesforcedata',
            name='opportunity_number',
            field=models.IntegerField(help_text=b'8 digit number starting with 201', unique=True, verbose_name=b'SF\\Opportunity Number', validators=[django.core.validators.MinValueValidator(20100000), django.core.validators.MaxValueValidator(99999999)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='salesforcedata',
            name='probability',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='salesforcedata',
            name='start_date',
            field=models.DateField(null=True, verbose_name=b'Estimated Start Date', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='salesforcedata',
            name='value',
            field=models.DecimalField(null=True, verbose_name=b'Project Value(in $)', max_digits=20, decimal_places=5, blank=True),
            preserve_default=True,
        ),
    ]
