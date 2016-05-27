# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('CompanyMaster', '0023_auto_20150804_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessunit',
            name='new_bu_head',
            field=models.ManyToManyField(related_name='New BU Head', null=True, verbose_name=b'Business Unit Head', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
    ]
