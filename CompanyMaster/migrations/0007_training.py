# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('CompanyMaster', '0006_auto_20150128_1541'),
    ]

    operations = [
        migrations.CreateModel(
            name='Training',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('batch', models.CharField(default=None, max_length=30, verbose_name=b'Batch')),
                ('exercise', models.CharField(default=None, max_length=30, verbose_name=b'Exercise')),
                ('trainingDate', models.DateField(verbose_name=b'Training Date')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('location', models.ForeignKey(verbose_name=b'Location', to='CompanyMaster.OfficeLocation')),
                ('trainer', models.ForeignKey(verbose_name=b'Trainer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
