# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0007_training'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='seqNumber',
            field=models.PositiveIntegerField(default=1, verbose_name=b'Project ID Sequence'),
            preserve_default=True,
        ),
    ]
