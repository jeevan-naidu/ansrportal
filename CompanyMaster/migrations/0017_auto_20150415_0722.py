# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0016_hractivity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessunit',
            name='bu_head',
            field=models.OneToOneField(null=True, blank=True, to=settings.AUTH_USER_MODEL, verbose_name=b'Business Unit Head'),
            preserve_default=True,
        ),
    ]
