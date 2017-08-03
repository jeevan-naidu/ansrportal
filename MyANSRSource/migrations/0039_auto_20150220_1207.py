# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0038_auto_20150220_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheetentry',
            name='chapter',
            field=models.ForeignKey(verbose_name=b'Chapter/Subtitle', to='MyANSRSource.Chapter', null=True),
            preserve_default=True,
        ),
    ]
