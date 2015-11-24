# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0099_projecttype_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectteammember',
            name='plannedEffort',
            field=models.DecimalField(default=0, verbose_name=b'Planned Effort', max_digits=12, decimal_places=2, blank=True),
            preserve_default=True,
        ),
    ]
