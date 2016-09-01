# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0028_department_department_head'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='department_centre_type',
            field=models.CharField(default='P', max_length=200, choices=[(b'P', b'Profit Center'), (b'C', b'Cost Center')]),
            preserve_default=False,
        ),
    ]
