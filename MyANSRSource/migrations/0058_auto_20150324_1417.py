# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0057_remove_projectteammember_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='po',
            field=models.CharField(default=0, max_length=60, verbose_name=b'P.O.', validators=[django.core.validators.RegexValidator(b'^[0-9a-zA-Z-]*$', b'Only alphanumeric characters are allowed.')]),
            preserve_default=True,
        ),
    ]
