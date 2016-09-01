# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('employee', '0020_employee_is_360eligible'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='peers',
            field=models.ManyToManyField(related_name='peers', default=None, to=settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name=b'Peer(s)'),
            preserve_default=True,
        ),
    ]
