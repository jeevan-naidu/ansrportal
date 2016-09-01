# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0043_auto_20151006_1129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fb360',
            name='year',
        ),
    ]
