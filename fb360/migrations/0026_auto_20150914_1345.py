# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0025_fb360_process_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualitativeresponse',
            name='submitted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='response',
            name='submitted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
