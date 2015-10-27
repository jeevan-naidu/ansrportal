# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('MyANSRSource', '0098_auto_20150923_1734'),
    ]

    operations = [
        migrations.CreateModel(
            name='RevenueRecognition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('btg', models.IntegerField(default=0, verbose_name=b'Current Month BTG', validators=[django.core.validators.MinValueValidator(0)])),
                ('btg_future', models.IntegerField(default=0, verbose_name=b'Current Current Month BTG', validators=[django.core.validators.MinValueValidator(0)])),
                ('estimated_effort', models.IntegerField(default=0, verbose_name=b'Total Estimated Effort', validators=[django.core.validators.MinValueValidator(0)])),
                ('status', models.IntegerField(default=0, verbose_name=b'Overrun/Underrun', validators=[django.core.validators.MinValueValidator(0)])),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedOn', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('member', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(verbose_name=b'Project Name', to='MyANSRSource.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='btgreport',
            name='member',
        ),
        migrations.RemoveField(
            model_name='btgreport',
            name='project',
        ),
        migrations.DeleteModel(
            name='BTGReport',
        ),
    ]
