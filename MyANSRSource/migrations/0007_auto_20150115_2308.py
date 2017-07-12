# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0006_auto_20150115_0940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='totalValue',
            field=models.DecimalField(default=0, verbose_name=b'Total Value', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectchangeinfo',
            name='revisedTotal',
            field=models.DecimalField(default=0, verbose_name=b'Revised amount', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectmilestone',
            name='amount',
            field=models.DecimalField(default=0, verbose_name=b'Amount', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
    ]
