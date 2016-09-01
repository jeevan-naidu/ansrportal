# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0021_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='projectManager',
            field=models.ForeignKey(verbose_name=b'Project Leader', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
