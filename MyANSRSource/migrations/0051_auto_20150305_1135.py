# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def populateValues(apps, schema_editor):
    projectObj = apps.get_model("MyANSRSource", "Project")
    pmObj = apps.get_model("MyANSRSource", "ProjectManager")

    projectInfo = projectObj.objects.all().values('projectManager', 'id')

    for eachInfo in projectInfo:
        pm = pmObj()
        pm.user_id = eachInfo['projectManager']
        pm.project_id = eachInfo['id']
        pm.save()


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0050_auto_20150305_1132'),
    ]

    operations = [
        migrations.RunPython(populateValues, ),
    ]
