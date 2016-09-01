# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def populateValues(apps, schema_editor):
    pass



class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0032_auto_20150218_1840'),
    ]

    operations = [
        migrations.RunPython(populateValues, ),
    ]
