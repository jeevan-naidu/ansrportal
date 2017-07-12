# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0053_auto_20150305_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='currentProject',
            field=models.BooleanField(default=True, verbose_name=b'New Development'),
            preserve_default=True,
        ),
    ]
