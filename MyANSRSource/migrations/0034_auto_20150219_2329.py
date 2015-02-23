# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, IntegrityError


def populateValues(apps, schema_editor):
    tsModel = apps.get_model("MyANSRSource", "TimeSheetEntry")
    activityModel = apps.get_model("MyANSRSource", "Activity")
    taskModel = apps.get_model("MyANSRSource", "Task")

    ts = tsModel.objects.filter(project__isnull=False).values('activity',
                                                              'task',
                                                              'project__projectType')
    for eachTs in ts:
        try:
            act = activityModel.objects.create(code=eachTs['activity'],
                                               name=eachTs['activity'])
            eachTs.activity1 = act
            act.save()
        except IntegrityError:
            pass
        try:
            tsk = taskModel.objects.create(code=eachTs['task'],
                                           name=eachTs['task'],
                                           projectType.id=eachTs['project__projectType'])
            eachTs.task1 = tsk
            tsk.save()
        except IntegrityError:
            pass
        eachTs.save()


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0042_auto_20150222_1937'),
        ('MyANSRSource', '0026_auto_20150217_1621'),
        ('MyANSRSource', '0027_auto_20150217_1629'),
    ]

    operations = [
        migrations.RunPython(populateValues, ),
    ]
