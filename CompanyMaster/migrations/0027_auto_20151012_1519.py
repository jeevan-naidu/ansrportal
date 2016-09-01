# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0026_remove_businessunit_bu_head'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datapoint',
            options={'verbose_name': 'Service Line', 'verbose_name_plural': 'Service Lines'},
        ),
    ]
