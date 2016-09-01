# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0024_auto_20150912_2120'),
    ]

    operations = [
        migrations.AddField(
            model_name='fb360',
            name='process_start_date',
            field=models.DateField(default=None, verbose_name=b'Process Start Date'),
            preserve_default=True,
        ),
    ]
