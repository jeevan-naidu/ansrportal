# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def populateValues(apps, schema_editor):
    tsModel = apps.get_model("MyANSRSource", "TimeSheetEntry")
    activityModel = apps.get_model("MyANSRSource", "Activity")
    taskModel = apps.get_model("MyANSRSource", "Task")

    ts = tsModel.objects.all().values('id', 'task', 'activity')
    for eachData in ts:
        act = activityModel.objects.get(code=eachData['activity'])
        tsk = taskModel.objects.get(code=eachData['task'])
        tsObj = tsModel.objects.get(pk=ts.id)
        tsObj.update(activity=act, task=tsk)
        tsObj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0032_auto_20150218_1840'),
    ]

    operations = [
        migrations.RunPython(populateValues, ),
    ]
