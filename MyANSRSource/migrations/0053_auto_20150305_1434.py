# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('MyANSRSource', '0052_auto_20150305_1146'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='chapters',
        ),
        migrations.RemoveField(
            model_name='project',
            name='pm',
        ),
        migrations.AddField(
            model_name='project',
            name='projectManager',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name=b'Project Leader', through='MyANSRSource.ProjectManager'),
            preserve_default=True,
        ),
    ]
