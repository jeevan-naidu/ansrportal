# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0046_fb360_eligible'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='respondent',
            unique_together=set([('employee', 'initiator', 'respondent_type')]),
        ),
    ]
