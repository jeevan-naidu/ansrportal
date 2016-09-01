# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0110_project_customer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='customer',
        ),
    ]
