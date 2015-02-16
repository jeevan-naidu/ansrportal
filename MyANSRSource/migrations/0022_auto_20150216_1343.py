# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0021_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'verbose_name': 'Book/Title', 'verbose_name_plural': 'Books/Titles'},
        ),
        migrations.AlterModelOptions(
            name='chapter',
            options={'verbose_name': 'Chapter/Subtitle', 'verbose_name_plural': 'Chapters/Subtitles'},
        ),
    ]
