# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0041_book_edition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='projectId',
            field=models.CharField(max_length=60, verbose_name=b'Project Code'),
            preserve_default=True,
        ),
    ]
