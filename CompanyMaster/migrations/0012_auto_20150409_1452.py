# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0011_businessunit_bu_head'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name=b'Type of Customer')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='customer',
            name='CType',
            field=models.ForeignKey(default=None, verbose_name=b'Customer Type', to='CompanyMaster.CustomerType'),
            preserve_default=True,
        ),
    ]
