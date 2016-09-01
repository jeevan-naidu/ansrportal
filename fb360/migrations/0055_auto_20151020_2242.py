# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0054_auto_20151016_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='fb1',
            field=models.ManyToManyField(default=None, related_name='New FB', to='fb360.FB360'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='question',
            name='group1',
            field=models.ManyToManyField(default=None, related_name='New Group', to='fb360.Group'),
            preserve_default=True,
        ),
    ]
