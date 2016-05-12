# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Leave', '0003_auto_20160428_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaveapplications',
            name='reason',
            field=models.CharField(max_length=1000, null=True, verbose_name=b'Reason', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='leavetype',
            name='leave_type',
            field=models.CharField(max_length=50, verbose_name=b'Leave Types', choices=[(b'earned_leave', b'Earned Leave'), (b'sick_leave', b'Sick Leave'), (b'casual_leave', b'Casual Leave'), (b'loss_of_pay', b'Loss Of Pay'), (b'bereavement_leave', b'Bereavement Leave'), (b'maternity_leave', b'Maternity Leave'), (b'paternity_leave', b'Paternity Leave'), (b'comp_off_apply', b'Comp Off Apply'), (b'comp_off_avail', b'Comp Off Avail'), (b'work_from_home', b'Work From Home'), (b'sabbatical', b'Sabbatical')]),
            preserve_default=True,
        ),
    ]
