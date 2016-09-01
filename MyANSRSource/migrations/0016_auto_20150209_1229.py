# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0015_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectmilestone',
            name='financial',
            field=models.BooleanField(default=False, verbose_name=b'Financial'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='signed',
            field=models.BooleanField(default=True, verbose_name=b'Contract Signed'),
            preserve_default=True,
        ),
    ]
