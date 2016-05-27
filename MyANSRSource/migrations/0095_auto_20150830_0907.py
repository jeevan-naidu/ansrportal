# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0094_auto_20150830_0850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='day',
            field=models.IntegerField(default=0, max_length=2, verbose_name=b'Day', choices=[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16), (16, 17), (17, 18), (18, 19), (19, 20), (20, 21), (21, 22), (22, 23), (23, 24), (24, 25), (25, 26), (26, 27), (27, 28), (28, 29), (29, 30)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='report',
            name='weekday',
            field=models.IntegerField(default=0, max_length=2, verbose_name=b'Weekday', choices=[(0, b'Monday'), (1, b'Tuesday'), (2, b'Wednesday'), (3, b'Thursday'), (4, b'Friday'), (5, b'Saturday'), (6, b'Sunday')]),
            preserve_default=True,
        ),
    ]
