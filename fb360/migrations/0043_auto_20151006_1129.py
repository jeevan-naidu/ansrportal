# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb360', '0042_auto_20151006_1121'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='managerrequest',
            name='respondent',
        ),
        migrations.DeleteModel(
            name='ManagerRequest',
        ),
        migrations.AddField(
            model_name='respondent',
            name='respondent_type',
            field=models.CharField(default=b'P', max_length=1, verbose_name=b'Respondent Type', choices=[(b'P', b'Peer'), (b'E', b'Reportee'), (b'M', b'Manager')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='respondent',
            name='initiator',
            field=models.ForeignKey(related_name='Pempl', default=None, verbose_name=b'Initiator', to='fb360.Initiator'),
            preserve_default=True,
        ),
    ]
