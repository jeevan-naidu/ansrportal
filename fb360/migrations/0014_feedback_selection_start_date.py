# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0013_auto_20150904_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='selection_start_date',
            field=models.DateField(default=None, verbose_name=b'Peer selection start date'),
            preserve_default=True,
        ),
    ]
