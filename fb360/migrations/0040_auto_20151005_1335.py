# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0039_fb360_eligible'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fb360',
            name='eligible',
            field=models.ManyToManyField(default=None, to='employee.Employee', verbose_name=b'Eligible Person(s)'),
            preserve_default=True,
        ),
    ]
