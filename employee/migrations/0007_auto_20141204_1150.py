# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0006_auto_20141204_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='designation',
            name='billable',
            field=models.BooleanField(default=True, verbose_name=b'Billable'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='employee',
            name='permanent_address',
            field=models.OneToOneField(related_name='permanent_addr', verbose_name=b'Permanent Address', to='employee.EmpAddress'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='employee',
            name='temporary_address',
            field=models.OneToOneField(related_name='temporary_addr', verbose_name=b'Temporary Address', to='employee.EmpAddress'),
            preserve_default=True,
        ),
    ]
