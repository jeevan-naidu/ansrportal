# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0011_auto_20150902_1915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emppeer',
            name='employee',
            field=models.ForeignKey(related_name='emp', default=None, to=settings.AUTH_USER_MODEL, unique=True),
            preserve_default=True,
        ),
    ]
