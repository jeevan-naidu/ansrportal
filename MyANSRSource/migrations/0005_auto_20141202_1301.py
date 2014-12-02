# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0004_auto_20141202_1300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='currentProject',
            field=models.BooleanField(verbose_name=b'Is this a new project?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='internal',
            field=models.BooleanField(verbose_name=b'Is this an internal project?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='signed',
            field=models.BooleanField(verbose_name=b'Is this project signed?'),
            preserve_default=True,
        ),
    ]
