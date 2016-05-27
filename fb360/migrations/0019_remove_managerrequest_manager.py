# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0018_managerrequest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='managerrequest',
            name='manager',
        ),
    ]
