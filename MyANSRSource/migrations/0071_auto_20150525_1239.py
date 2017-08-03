# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0070_auto_20150520_2241'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='task',
            unique_together=set([('projectType', 'name'), ('projectType', 'code')]),
        ),
    ]
