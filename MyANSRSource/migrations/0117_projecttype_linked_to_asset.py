# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0116_auto_20160809_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='projecttype',
            name='linked_to_asset',
            field=models.CharField(blank=True, max_length=10, null=True, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
            preserve_default=True,
        ),
    ]
