# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0012_remove_projectmilestone_deliverables'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectteammember',
            name='rate',
            field=models.IntegerField(default=100, verbose_name=b'%'),
            preserve_default=True,
        ),
    ]
