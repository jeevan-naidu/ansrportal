# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0004_auto_20141203_1901'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='education',
            options={'verbose_name': 'Education', 'verbose_name_plural': 'Education'},
        ),
        migrations.AlterModelOptions(
            name='empaddress',
            options={'verbose_name_plural': 'Addresses'},
        ),
        migrations.AlterModelOptions(
            name='previousemployment',
            options={'verbose_name': 'Previous Employment', 'verbose_name_plural': 'Previous Employment'},
        ),
    ]
