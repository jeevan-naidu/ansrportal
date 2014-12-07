# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectchangeinfo',
            name='milestone',
        ),
        migrations.RemoveField(
            model_name='projectchangeinfo',
            name='teamMember',
        ),
    ]
