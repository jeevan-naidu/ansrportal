# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('MyANSRSource', '0075_auto_20150618_1001'),
    ]

    operations = [
        migrations.CreateModel(
            name='BTGReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lastMonthAE', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('currMonthAE', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('btg', models.IntegerField(default=0, verbose_name=b'BTG', validators=[django.core.validators.MinValueValidator(0)])),
                ('lastMonthRR', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('currMonthRR', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('lastMonthIN', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('currMonthIN', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('member', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(verbose_name=b'Project Name', to='MyANSRSource.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
