# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0006_auto_20150902_1049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='approval_date',
            field=models.DateField(verbose_name=b'Peer approval completion date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='feedback',
            name='end_date',
            field=models.DateField(verbose_name=b'Complete 360 degree appraisal'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='feedback',
            name='selection_date',
            field=models.DateField(verbose_name=b'Peer selection completion date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='feedback',
            name='start_date',
            field=models.DateField(verbose_name=b'Start 360 degree appraisal'),
            preserve_default=True,
        ),
    ]
