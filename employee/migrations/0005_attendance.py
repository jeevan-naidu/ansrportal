# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0004_auto_20150216_1156'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('swipe_in', models.DateTimeField(null=True, blank=True)),
                ('swipe_out', models.DateTimeField(null=True, blank=True)),
                ('swipe_location', models.CharField(max_length=100, null=True, blank=True)),
                ('employee', models.ForeignKey(to='employee.Employee')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
