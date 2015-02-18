# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def populateValues(apps, schema_editor):
    ts = apps.get_model("MyANSRSource", "TimeSheetEntry")
    activity = apps.get_model("MyANSRSource", "Activity")
    task = apps.get_model("MyANSRSource", "Activity")

    for eachTs in ts:
        activity.code = eachTs.activity
        task.code = eachTs.task
        task.save()
        activity.save()


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0032_auto_20150218_1840'),
    ]

    operations = [
        migrations.RunPython(populateValues),
    ]
