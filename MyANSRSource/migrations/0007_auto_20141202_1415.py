# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0006_auto_20141202_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='currentProject',
            field=models.BooleanField(default=False, verbose_name=b'Project Stage'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='internal',
            field=models.BooleanField(default=False, verbose_name=b'Internal Project'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='signed',
            field=models.BooleanField(default=False, verbose_name=b'project Signed'),
            preserve_default=True,
        ),
    ]
