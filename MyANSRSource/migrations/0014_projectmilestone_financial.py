# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0013_project_maxproductivityunits'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectmilestone',
            name='financial',
            field=models.BooleanField(default=False, verbose_name=b'Financial Milestone?'),
            preserve_default=True,
        ),
    ]
