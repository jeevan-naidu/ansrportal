# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, IntegrityError


def populateValues(apps, schema_editor):
    tsModel = apps.get_model("MyANSRSource", "TimeSheetEntry")
    activityModel = apps.get_model("MyANSRSource", "Activity")
    taskModel = apps.get_model("MyANSRSource", "Task")

    ts = tsModel.objects.all().values('task', 'activity')
    for eachData in ts:
        try:
            act = activityModel.objects.create(code=eachData['activity'])
            ts.activity1 = act
            act.save()
        except IntegrityError:
            pass
        try:
            tsk = taskModel.objects.create(code=eachData['task'])
            ts.task1 = tsk
            tsk.save()
        except IntegrityError:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0042_auto_20150222_1937'),
    ]

    operations = [
        migrations.RunPython(populateValues, ),
    ]
