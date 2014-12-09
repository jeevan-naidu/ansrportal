# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyANSRSource', '0003_auto_20141206_2123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheetentry',
            name='location',
            field=models.ForeignKey(verbose_name=b'Location', to='CompanyMaster.OfficeLocation', null=True),
            preserve_default=True,
        ),
        migrations.DeleteModel(
            name='Location',
        ),
    ]
