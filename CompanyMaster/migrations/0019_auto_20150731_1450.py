# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('CompanyMaster', '0018_remove_customer_relatedmember'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='Cdelivery',
            field=models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True, verbose_name=b'Account delivery manager'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customer',
            name='Crelation',
            field=models.ForeignKey(related_name='Relation', default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True, verbose_name=b'Account relationship manager'),
            preserve_default=True,
        ),
    ]
