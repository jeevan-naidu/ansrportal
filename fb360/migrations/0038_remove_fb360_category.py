# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0037_qualitativeresponse_qst'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fb360',
            name='category',
        ),
    ]
