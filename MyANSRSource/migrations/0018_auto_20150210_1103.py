# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0017_timesheetentry_toapprove'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheetentry',
            name='fridayH',
            field=models.DecimalField(default=0.0, verbose_name=b'Fri', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='mondayH',
            field=models.DecimalField(default=0.0, verbose_name=b'Mon', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='saturdayH',
            field=models.DecimalField(default=0.0, verbose_name=b'Sat', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='sundayH',
            field=models.DecimalField(default=0.0, verbose_name=b'Sun', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='thursdayH',
            field=models.DecimalField(default=0.0, verbose_name=b'Thu', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='totalH',
            field=models.DecimalField(default=0.0, verbose_name=b'Total', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='tuesdayH',
            field=models.DecimalField(default=0.0, verbose_name=b'Tue', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timesheetentry',
            name='wednesdayH',
            field=models.DecimalField(default=0.0, verbose_name=b'Wed', max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
    ]
