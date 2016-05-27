# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0033_question_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='fb',
            field=models.ForeignKey(default=None, to='fb360.FB360'),
            preserve_default=True,
        ),
    ]
