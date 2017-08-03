# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0086_remove_project_maxproductivityunits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(unique=True, max_length=50, verbose_name=b'Project Name'),
            preserve_default=True,
        ),
    ]
