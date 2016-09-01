# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0031_auto_20160808_1716'),
        ('employee', '0028_remove_employee_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='location',
            field=models.ForeignKey(blank=True, to='CompanyMaster.Location', null=True),
            preserve_default=True,
        ),
    ]
