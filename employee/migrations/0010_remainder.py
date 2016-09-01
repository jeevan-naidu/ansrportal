# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0009_auto_20150326_1552'),
    ]

    operations = [
        migrations.CreateModel(
            name='Remainder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=b'100', verbose_name=b'Event Name')),
                ('date', models.DateField(verbose_name=b'Date')),
                ('color', models.CharField(max_length=b'10', verbose_name=b'Color')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
