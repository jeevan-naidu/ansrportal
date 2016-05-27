# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('MyANSRSource', '0066_projectchangeinfo_po'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='customerContact',
            field=models.ForeignKey(related_name='Cusomer Contact', default=None, verbose_name=b'Customer Contact', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
