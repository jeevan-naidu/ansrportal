# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0040_auto_20151005_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='emppeer',
            name='survey',
            field=models.ForeignKey(default=None, to='fb360.FB360'),
            preserve_default=True,
        ),
    ]
