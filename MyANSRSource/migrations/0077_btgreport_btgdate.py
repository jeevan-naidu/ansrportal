# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0076_btgreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='btgreport',
            name='btgDate',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
    ]
