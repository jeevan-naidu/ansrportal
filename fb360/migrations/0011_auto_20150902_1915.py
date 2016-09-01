# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0010_auto_20150902_1824'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='peer',
            unique_together=set([('employee', 'emppeer')]),
        ),
    ]
