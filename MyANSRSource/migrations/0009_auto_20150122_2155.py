# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0008_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='projectType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=2, verbose_name=b'Code')),
                ('description', models.CharField(max_length=100, verbose_name=b'Description')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='project',
            name='projectType',
            field=models.ForeignKey(verbose_name=b'Project Type', to='MyANSRSource.projectType'),
            preserve_default=True,
        ),
    ]
