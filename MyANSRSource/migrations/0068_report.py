# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('MyANSRSource', '0067_project_customercontact'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=None, max_length=100, verbose_name=b'Name')),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('notify', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name=b'Notifier(s)')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
