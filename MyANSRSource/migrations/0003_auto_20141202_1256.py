# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0002_auto_20141202_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='internal',
            field=models.BooleanField(default=False, verbose_name=b'Is this an internal project?'),
            preserve_default=True,
        ),
    ]
