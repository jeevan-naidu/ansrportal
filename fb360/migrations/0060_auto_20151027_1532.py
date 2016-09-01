# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0059_auto_20151023_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualitativeresponse',
            name='fb',
            field=models.ForeignKey(default=2, to='fb360.FB360', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='response',
            name='fb',
            field=models.ForeignKey(default=2, to='fb360.FB360', null=True),
            preserve_default=True,
        ),
    ]
