# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0028_remove_fb360_selection_start_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Name')),
                ('priority', models.IntegerField(max_length=100, verbose_name=b'Priority', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)])),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='fb360',
            options={'verbose_name': 'FB360 Information', 'verbose_name_plural': 'FB360 Information'},
        ),
    ]
