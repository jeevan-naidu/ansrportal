# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0002_auto_20150901_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='ans1',
            field=models.ForeignKey(related_name='ansr_new', default=None, verbose_name=b'Choice', to='fb360.Answer'),
            preserve_default=True,
        ),
    ]
