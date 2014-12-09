# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0009_auto_20141209_1629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='closed',
            field=models.BooleanField(default=False, verbose_name=b'Project Closed'),
            preserve_default=True,
        ),
    ]
