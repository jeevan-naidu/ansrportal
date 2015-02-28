# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, IntegrityError, transaction


def populateValues(apps, schema_editor):
    tsModel = apps.get_model("MyANSRSource", "TimeSheetEntry")
    ptModel = apps.get_model("MyANSRSource", "projectType")
    activityModel = apps.get_model("MyANSRSource", "Activity")
    taskModel = apps.get_model("MyANSRSource", "Task")

    activityts = tsModel.objects.filter(billable=False)
    for eachTs in activityts:
        try:
            with transaction.atomic():
                act = activityModel.objects.create(code=eachTs.activity,
                                                   name=eachTs.activity)
                act.save()
                eachTs.activity1 = act
        except IntegrityError:
            eachTs.activity1 = activityModel.objects.get(
                code=eachTs.activity)
        eachTs.save()

    projectts = tsModel.objects.filter(billable=True)
    for eachTs in projectts:
        try:
            with transaction.atomic():
                ptObj = ptModel.objects.get(
                    pk=int(eachTs.project.projectType.id))
                tsk = taskModel.objects.create(code=eachTs.task,
                                               name=eachTs.task,
                                               projectType=ptObj)
                tsk.save()
                eachTs.task1 = tsk
        except IntegrityError:
            eachTs.task1 = taskModel.objects.get(code=eachTs.task)
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
