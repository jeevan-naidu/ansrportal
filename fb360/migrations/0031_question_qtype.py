# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0030_remove_question_fb'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='qtype',
            field=models.CharField(default=b'Q', max_length=1, verbose_name=b'Type', choices=[(b'Q', b'Qualitative'), (b'M', b'Multiple Choice')]),
            preserve_default=True,
        ),
    ]
