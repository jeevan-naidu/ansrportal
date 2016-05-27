# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0056_auto_20151020_2243'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='fb',
        ),
        migrations.RemoveField(
            model_name='question',
            name='group',
        ),
    ]
