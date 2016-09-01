# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('employee', '0021_employee_peers'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='reportees',
            field=models.ManyToManyField(related_name='reportees', default=None, to=settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name=b'Reportee(s)'),
            preserve_default=True,
        ),
    ]
