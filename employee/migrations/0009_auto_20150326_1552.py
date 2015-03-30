# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0008_attendance_incoming_employee_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attendance',
            options={'verbose_name': 'Attendance', 'verbose_name_plural': 'Attendance'},
        ),
        migrations.AlterField(
            model_name='attendance',
            name='attdate',
            field=models.DateField(null=True, verbose_name=b'Swipe Date', blank=True),
            preserve_default=True,
        ),
    ]
