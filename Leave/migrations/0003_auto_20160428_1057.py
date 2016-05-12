# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import Leave.models


class Migration(migrations.Migration):

    dependencies = [
        ('Leave', '0002_auto_20160420_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaveapplications',
            name='atachement',
            field=models.FileField(upload_to=Leave.models.content_file_name, null=True, verbose_name=b'Attachment', blank=True),
            preserve_default=True,
        ),
    ]
