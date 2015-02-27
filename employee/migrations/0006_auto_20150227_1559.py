# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0005_attendance'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='attdate',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='attendance',
            name='employee',
            field=models.ForeignKey(to='employee.Employee', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together=set([('employee', 'attdate')]),
        ),
    ]
