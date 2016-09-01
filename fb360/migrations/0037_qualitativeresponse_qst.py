# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0036_question_priority'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualitativeresponse',
            name='qst',
            field=models.ForeignKey(default=None, to='fb360.Question'),
            preserve_default=True,
        ),
    ]
