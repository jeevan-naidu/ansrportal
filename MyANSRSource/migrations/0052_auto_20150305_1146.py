# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0051_auto_20150305_1135'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='projectManager',
        ),
        migrations.AlterField(
            model_name='project',
            name='pm',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name=b'Project Leader', through='MyANSRSource.ProjectManager'),
            preserve_default=True,
        ),
    ]
