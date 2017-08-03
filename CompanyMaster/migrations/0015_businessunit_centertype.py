# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0014_auto_20150409_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessunit',
            name='centerType',
            field=models.CharField(default=None, max_length=2, verbose_name=b'Type of center', choices=[(b'P', b'Profit Center'), (b'C', b'Cost Center')]),
            preserve_default=True,
        ),
    ]
