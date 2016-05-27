# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0021_question_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fb360',
            options={'verbose_name': 'FB360 Information', 'verbose_name_plural': 'FB360 Informations'},
        ),
    ]
