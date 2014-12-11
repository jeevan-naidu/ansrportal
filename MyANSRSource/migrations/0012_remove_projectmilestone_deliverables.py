# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0011_auto_20141209_1631'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectmilestone',
            name='deliverables',
        ),
    ]
