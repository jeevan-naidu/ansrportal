# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0092_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='weekday',
            field=models.CharField(default=b'0', max_length=2, verbose_name=b'Weekday', choices=[(0, b'Monday'), (1, b'Tuesday'), (2, b'Wednesday'), (3, b'Thursday'), (4, b'Friday'), (5, b'Saturday'), (6, b'Sunday')]),
            preserve_default=True,
        ),
    ]
