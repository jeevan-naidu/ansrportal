# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def populateValues(apps, schema_editor):

    # Copying FK values to M2M for group model's
    # fb field
    groupModel = apps.get_model("fb360", "Group")
    groupObj = groupModel.objects.all()

    for eachObj in groupObj:
        eachObj.fb1.add(eachObj.fb)
        eachObj.save()

    # Copying FK values to M2M for question model's
    # group field
    qstModel = apps.get_model("fb360", "Question")
    qstObj = qstModel.objects.all()
    for eachObj in qstObj:
        eachObj.group1.add(eachObj.group)
        eachObj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0055_auto_20151020_2242'),
    ]

    operations = [
        migrations.RunPython(populateValues, ),
    ]
