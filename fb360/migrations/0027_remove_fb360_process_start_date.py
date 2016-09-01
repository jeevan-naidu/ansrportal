# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0026_auto_20150914_1345'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fb360',
            name='process_start_date',
        ),
    ]
