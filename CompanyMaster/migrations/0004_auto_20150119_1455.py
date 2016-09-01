# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0003_auto_20150119_1454'),
    ]

    operations = [
        migrations.RenameField(
            model_name='holiday',
            old_name='location1',
            new_name='location',
        ),
    ]
