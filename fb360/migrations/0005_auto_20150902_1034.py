# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0004_remove_question_ans'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='ans1',
            new_name='ans',
        ),
    ]
