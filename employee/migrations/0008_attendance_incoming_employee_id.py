# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0007_remove_attendance_swipe_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='incoming_employee_id',
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
    ]
