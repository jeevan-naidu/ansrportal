# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0007_auto_20150902_1055'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='peer',
            name='year',
        ),
        migrations.AlterField(
            model_name='emppeer',
            name='peer',
            field=models.ManyToManyField(default=None, related_name='Epeer', verbose_name=b'Choose Peer', through='fb360.Peer', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
