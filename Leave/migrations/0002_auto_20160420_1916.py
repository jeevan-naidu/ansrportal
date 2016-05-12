# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Leave', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaveSummary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.CharField(max_length=10, verbose_name=b'Current Year')),
                ('applied', models.CharField(max_length=20, verbose_name=b'applied leave count')),
                ('approved', models.CharField(max_length=20, verbose_name=b'approved leave count')),
                ('balance', models.CharField(max_length=20, verbose_name=b'balance leave count')),
                ('type', models.ForeignKey(verbose_name=b'Leave Type', to='Leave.LeaveType')),
                ('user', models.ForeignKey(verbose_name=b'User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='leaveapplications',
            name='from_session',
            field=models.CharField(max_length=20, verbose_name=b'Leave From session', choices=[(b'session_first', b'Session First'), (b'session_second', b'Session Second')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='leaveapplications',
            name='to_session',
            field=models.CharField(max_length=20, verbose_name=b'Leave To session', choices=[(b'session_first', b'Session First'), (b'session_second', b'Session Second')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='leavetype',
            name='leave_type',
            field=models.CharField(max_length=20, verbose_name=b'Leave Types', choices=[(b'earned_leave', b'Earned Leave'), (b'sick_leave', b'Sick Leave'), (b'casual_leave', b'Casual Leave'), (b'loss_of_pay', b'Loss Of Pay'), (b'bereavement_leaves', b'Bereavement Leave'), (b'maternity_leave', b'Maternity Leave'), (b'paternity_leave', b'Paternity Leave'), (b'comp_off_apply', b'Comp Off Apply'), (b'comp_off_avail', b'Comp Off Avail'), (b'work_from_home', b'Work From Home'), (b'sabbatical', b'Sabbatical')]),
            preserve_default=True,
        ),
    ]
