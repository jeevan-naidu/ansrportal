# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0049_auto_20151007_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fb360',
            name='approval_date',
            field=models.DateField(verbose_name=b'Peer / Reportee approval completion date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fb360',
            name='selection_date',
            field=models.DateField(verbose_name=b'Peer / Reportee selection completion date'),
            preserve_default=True,
        ),
    ]
