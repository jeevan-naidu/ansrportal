# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('CompanyMaster', '0010_customer_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessunit',
            name='bu_head',
            field=models.OneToOneField(default=None, verbose_name=b'Business Unit Head', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
