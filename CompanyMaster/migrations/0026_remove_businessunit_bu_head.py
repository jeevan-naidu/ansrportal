# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0025_auto_20150807_1355'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='businessunit',
            name='bu_head',
        ),
    ]
