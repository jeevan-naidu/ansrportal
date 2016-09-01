# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0012_auto_20150204_1111'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='maxProductivityUnits',
            field=models.DecimalField(default=0.0, verbose_name=b'Norm', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
    ]
