# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0022_auto_20150911_1112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='fb',
            field=models.ForeignKey(default=None, verbose_name=b'FB360 Information', to='fb360.FB360'),
            preserve_default=True,
        ),
    ]
