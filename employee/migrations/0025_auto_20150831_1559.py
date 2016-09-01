# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0024_auto_20150831_1254'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='peer',
            name='receiver',
        ),
        migrations.RemoveField(
            model_name='peer',
            name='sender',
        ),
        migrations.DeleteModel(
            name='Peer',
        ),
    ]
