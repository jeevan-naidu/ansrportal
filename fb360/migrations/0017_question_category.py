# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0025_auto_20150831_1559'),
        ('fb360', '0016_remove_question_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='category',
            field=models.ForeignKey(default=None, to='employee.Designation'),
            preserve_default=True,
        ),
    ]
