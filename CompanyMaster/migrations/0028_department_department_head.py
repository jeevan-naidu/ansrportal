# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0026_auto_20151006_1216'),
        ('CompanyMaster', '0027_auto_20151012_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='department_head',
            field=models.ForeignKey(default=1006188, verbose_name=b'Head', to='employee.Employee'),
            preserve_default=False,
        ),
    ]
