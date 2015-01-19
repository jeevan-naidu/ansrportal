# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='holiday',
            name='location',
            field=models.ForeignKey(default=None, to='CompanyMaster.OfficeLocation'),
            preserve_default=True,
        ),
    ]
