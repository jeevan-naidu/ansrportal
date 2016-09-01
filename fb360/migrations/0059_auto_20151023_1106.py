# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0058_auto_20151020_2310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fb360',
            name='approval_date',
            field=models.DateField(verbose_name=b'Peer / Reportee / Additional Manager approval completion date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fb360',
            name='selection_date',
            field=models.DateField(verbose_name=b'Peer / Reportee / Additional Manager selection completion date'),
            preserve_default=True,
        ),
    ]
