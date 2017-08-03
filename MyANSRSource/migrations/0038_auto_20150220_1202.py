# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0037_auto_20150220_1152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='name',
            field=models.CharField(max_length=100, verbose_name=b'Name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='book',
            field=models.ForeignKey(default=None, verbose_name=b'Book/Title', to='MyANSRSource.Book'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='chapters',
            field=models.ManyToManyField(to='MyANSRSource.Chapter', verbose_name=b'Chapter/Subtitle'),
            preserve_default=True,
        ),
    ]
