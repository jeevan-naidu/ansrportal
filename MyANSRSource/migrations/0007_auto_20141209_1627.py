# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0006_auto_20141209_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='closed',
            field=models.BooleanField(verbose_name=b'Project Closed'),
            preserve_default=True,
        ),
    ]
