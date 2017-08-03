# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0015_businessunit_centertype'),
    ]

    operations = [
        migrations.CreateModel(
            name='HRActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=None, max_length=b'100', verbose_name=b'Event Name')),
                ('date', models.DateField(verbose_name=b'Event Date')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
            ],
            options={
                'verbose_name': 'HR Activity',
                'verbose_name_plural': 'HR Activities',
            },
            bases=(models.Model,),
        ),
    ]
