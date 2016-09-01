# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0022_auto_20150216_1600'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Activity')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Task')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('projectype', models.ForeignKey(verbose_name=b'Project Type', to='MyANSRSource.projectType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
