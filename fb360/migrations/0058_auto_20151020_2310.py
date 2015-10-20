# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0057_auto_20151020_2307'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='fb1',
            new_name='fb',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='group1',
            new_name='group',
        ),
    ]
