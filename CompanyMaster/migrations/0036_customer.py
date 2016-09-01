# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0030_auto_20160808_1858'),
        ('CompanyMaster', '0035_auto_20160808_1905'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('customer_code', models.CharField(max_length=200, verbose_name=b'Customer Code')),
                ('customer_name', models.CharField(max_length=200, verbose_name=b'Customer Name')),
                ('project_id_sequence', models.PositiveIntegerField(verbose_name=b'Project ID Sequence')),
                ('customer_contact', models.CharField(max_length=200, null=True, verbose_name=b'Customer Contact', blank=True)),
                ('bill_to_email', models.EmailField(max_length=200, null=True, verbose_name=b'Bill To Email', blank=True)),
                ('ship_to_email', models.EmailField(max_length=200, null=True, verbose_name=b'Ship To Email', blank=True)),
                ('internal', models.BooleanField(default=False, verbose_name=b'Internal Customer')),
                ('account_receivable_email', models.EmailField(max_length=200, null=True, verbose_name=b'Account Receivable Email', blank=True)),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
                ('HQ_address', models.ForeignKey(related_name='HQ Address', to='CompanyMaster.Location')),
                ('account_delivery_manager', models.ForeignKey(related_name='Account Delivery Manager', blank=True, to='employee.Employee', null=True)),
                ('account_relationship_manager', models.ForeignKey(related_name='Account Relationship Manager', blank=True, to='employee.Employee', null=True)),
                ('bill_to_address', models.ForeignKey(related_name='Bill To Address', blank=True, to='CompanyMaster.Location', null=True)),
                ('business_segment', models.ForeignKey(to='CompanyMaster.BusinessSegment')),
                ('customer_type', models.ForeignKey(to='CompanyMaster.CustomerType')),
                ('group_customer_name', models.ForeignKey(blank=True, to='CompanyMaster.GroupCustomer', null=True)),
                ('ship_to_address', models.ForeignKey(related_name='Ship To Address', blank=True, to='CompanyMaster.Location', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
