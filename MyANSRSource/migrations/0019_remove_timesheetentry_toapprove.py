# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0018_auto_20150210_1103'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timesheetentry',
            name='toApprove',
        ),
    ]