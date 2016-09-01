# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core.exceptions import ObjectDoesNotExist


def populateValues(apps, schema_editor):
    buModel = apps.get_model("CompanyMaster", "BusinessUnit")
    bu = buModel.objects.all().values('id', 'bu_head')
    if len(bu):
        for eachBU in bu:
            try:
                updateBU = buModel.objects.get(pk=eachBU['id'])
                updateBU.new_bu_head.add(eachBU['bu_head'])
                updateBU.save()
            except ObjectDoesNotExist:
                pass
    else:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0024_businessunit_new_bu_head'),
    ]

    operations = [
        migrations.RunPython(populateValues, ),
    ]
