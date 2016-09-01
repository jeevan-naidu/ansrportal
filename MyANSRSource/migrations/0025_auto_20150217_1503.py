# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0024_auto_20150217_1500'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='projectype',
            new_name='projectType',
        ),
    ]
