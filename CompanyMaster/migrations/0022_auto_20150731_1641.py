# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('CompanyMaster', '0021_datapoints'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40, verbose_name=b'Service Line')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('bu', models.ForeignKey(verbose_name=b'BU', to='CompanyMaster.BusinessUnit')),
                ('lead', models.ForeignKey(verbose_name=b'Lead', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='datapoints',
            name='bu',
        ),
        migrations.RemoveField(
            model_name='datapoints',
            name='lead',
        ),
        migrations.DeleteModel(
            name='DataPoints',
        ),
    ]
