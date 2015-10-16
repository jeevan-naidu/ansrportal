# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0053_auto_20151016_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='respondent',
            name='respondent_type',
            field=models.CharField(default=b'P', max_length=2, verbose_name=b'Respondent Type', choices=[(b'P', b'Peer'), (b'E', b'Reportee'), (b'M', b'Manager'), (b'AM', b'Additional Manager')]),
            preserve_default=True,
        ),
    ]
