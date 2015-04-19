# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0011_remainder_employee'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='remainder',
            name='color',
        ),
    ]
