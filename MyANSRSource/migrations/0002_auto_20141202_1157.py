# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='currentProject',
            field=models.BooleanField(default=False, verbose_name=b'Is this a new project?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='internal',
            field=models.BooleanField(default=False, verbose_name=b'Is this internal project?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='signed',
            field=models.BooleanField(default=False, verbose_name=b'Is this project signed?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projectteammember',
            name='endDate',
            field=models.DateField(default=django.utils.timezone.now, verbose_name=b'End date on project'),
            preserve_default=True,
        ),
    ]
