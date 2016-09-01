# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0047_auto_20151007_1207'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='initiator',
            unique_together=set([('employee', 'survey')]),
        ),
    ]
