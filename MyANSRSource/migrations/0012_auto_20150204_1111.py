# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0011_auto_20150203_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheetentry',
            name='fridayQ',
            field=models.DecimalField(default=0.0, verbose_name=b'Fri', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='mondayQ',
            field=models.DecimalField(default=0.0, verbose_name=b'Mon', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='saturdayQ',
            field=models.DecimalField(default=0.0, verbose_name=b'Sat', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='sundayQ',
            field=models.DecimalField(default=0.0, verbose_name=b'Sun', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='thursdayQ',
            field=models.DecimalField(default=0.0, verbose_name=b'Thu', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='totalQ',
            field=models.DecimalField(default=0.0, verbose_name=b'Total', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='tuesdayQ',
            field=models.DecimalField(default=0.0, verbose_name=b'Tue', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='wednesdayQ',
            field=models.DecimalField(default=0.0, verbose_name=b'Wed', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
    ]
