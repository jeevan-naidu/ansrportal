# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0004_auto_20150114_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='endDate',
            field=models.DateField(verbose_name=b'Project End Date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='startDate',
            field=models.DateField(verbose_name=b'Project Start Date'),
            preserve_default=True,
        ),
    ]
