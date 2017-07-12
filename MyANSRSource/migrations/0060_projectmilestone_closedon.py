# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0059_auto_20150324_1419'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectmilestone',
            name='closedon',
            field=models.DateTimeField(default=None, verbose_name=b'Closed On', null=True, editable=False, blank=True),
            preserve_default=True,
        ),
    ]
