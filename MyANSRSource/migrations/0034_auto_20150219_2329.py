# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def populateValues(apps, schema_editor):
    tsModel = apps.get_model("MyANSRSource", "TimeSheetEntry")
    activityModel = apps.get_model("MyANSRSource", "Activity")
    taskModel = apps.get_model("MyANSRSource", "Task")

    ts = tsModel.objects.all().values('task', 'activity')
    for eachData in ts:
        act = activityModel.objects.create(code=eachData['activity'])
        tsk = taskModel.objects.create(code=eachData['task'])
        act.save()
        tsk.save()


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0023_activity_task'),
    ]

    operations = [
        migrations.RunPython(populateValues, ),
    ]
