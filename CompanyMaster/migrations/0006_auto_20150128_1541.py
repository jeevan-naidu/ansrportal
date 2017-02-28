# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0005_auto_20150122_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='relatedMember',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name=b'Select Account Relationship team'),
            preserve_default=True,
        ),
    ]