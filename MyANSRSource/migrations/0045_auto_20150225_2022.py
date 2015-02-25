# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0044_auto_20150225_1126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='code',
            field=models.CharField(default=None, max_length=1, verbose_name=b'Short Code'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='task',
            unique_together=set([('projectType', 'code')]),
        ),
    ]
