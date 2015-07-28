# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0083_auto_20150726_2339'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='book',
            unique_together=set([('name', 'edition')]),
        ),
    ]
