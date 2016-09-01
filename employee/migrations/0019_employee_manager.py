# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0018_designation_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='manager',
            field=models.ForeignKey(related_name='Manager', default=None, null=True, blank=True, verbose_name=b'Manager', to='employee.Employee'),
            preserve_default=True,
        ),
    ]
