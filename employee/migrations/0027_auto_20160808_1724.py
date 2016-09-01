# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0031_auto_20160808_1716'),
        ('employee', '0026_auto_20151006_1216'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='company',
            field=models.ForeignKey(verbose_name=b'Company Name', blank=True, to='CompanyMaster.Company', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='employee',
            name='pratice',
            field=models.ForeignKey(verbose_name=b'Practice', blank=True, to='CompanyMaster.Practice', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='employee',
            name='sub_practice',
            field=models.ForeignKey(verbose_name=b'Sub Practice', blank=True, to='CompanyMaster.SubPractice', null=True),
            preserve_default=True,
        ),
    ]
