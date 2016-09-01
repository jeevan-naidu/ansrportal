# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0048_auto_20151007_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='initiator',
            name='employee',
            field=models.ForeignKey(related_name='emp', default=None, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
