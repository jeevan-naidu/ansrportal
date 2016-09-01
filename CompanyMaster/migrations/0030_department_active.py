# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0029_department_department_centre_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='active',
            field=models.BooleanField(default=True, verbose_name=b'Is Active?'),
            preserve_default=True,
        ),
    ]
