# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0023_auto_20150911_1116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='managerrequest',
            name='respondent',
            field=models.ForeignKey(related_name='Rrespon', default=None, to=settings.AUTH_USER_MODEL, unique=True),
            preserve_default=True,
        ),
    ]
