# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0005_auto_20150902_1034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='ans',
        ),
        migrations.AddField(
            model_name='answer',
            name='qst',
            field=models.ForeignKey(related_name='ansr_new', default=None, verbose_name=b'Question', to='fb360.Question'),
            preserve_default=True,
        ),
    ]
