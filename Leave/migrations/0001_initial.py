# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import Leave.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaveApplications',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('from_date', models.DateField(verbose_name=b'Leave from Date')),
                ('from_session', models.CharField(max_length=20, verbose_name=b'', choices=[(b'session_first', b'First Half'), (b'session_second', b'Second Half')])),
                ('to_date', models.DateField(verbose_name=b'Leave to Date')),
                ('to_session', models.CharField(max_length=20, verbose_name=b'', choices=[(b'session_first', b'First Half'), (b'session_second', b'Second Half')])),
                ('reason', models.CharField(max_length=1000, null=True, verbose_name=b'Reason', blank=True)),
                ('status', models.CharField(max_length=100, verbose_name=b'Status Of Leave', choices=[(b'open', b'Open'), (b'approved', b'Approved'), (b'rejected', b'Rejected'), (b'cancelled', b'Cancelled')])),
                ('status_action_on', models.DateField(auto_now=True, verbose_name=b'Date of Change')),
                ('status_comments', models.CharField(max_length=500, verbose_name=b'Status change comment')),
                ('due_date', models.DateField(null=True, verbose_name=b'application of comp off')),
                ('days_count', models.CharField(max_length=10, verbose_name=b'Leave Count')),
                ('atachement', models.FileField(upload_to=Leave.models.content_file_name, null=True, verbose_name=b'Attachment', blank=True)),
                ('applied_on', models.DateField(auto_now_add=True, verbose_name=b'Leave Applied Date')),
                ('modified_on', models.DateField(auto_now=True, verbose_name=b'Modified Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
                ('apply_to', models.ForeignKey(related_name='manager', verbose_name=b'Manager', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LeaveSummary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.CharField(max_length=10, verbose_name=b'Current Year')),
                ('applied', models.CharField(max_length=20, verbose_name=b'applied leave count')),
                ('approved', models.CharField(max_length=20, verbose_name=b'approved leave count')),
                ('balance', models.CharField(max_length=20, verbose_name=b'balance leave count')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LeaveType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('leave_type', models.CharField(max_length=50, verbose_name=b'Leave Types', choices=[(b'earned_leave', b'Earned Leave'), (b'sick_leave', b'Sick Leave'), (b'casual_leave', b'Casual Leave'), (b'loss_of_pay', b'Loss Of Pay'), (b'bereavement_leave', b'Bereavement Leave'), (b'maternity_leave', b'Maternity Leave'), (b'paternity_leave', b'Paternity Leave'), (b'comp_off_earned', b'Comp Off Earned'), (b'comp_off_avail', b'Comp Off Avail'), (b'pay_off', b'Pay Off'), (b'work_from_home', b'Work From Home'), (b'sabbatical', b'Sabbatical')])),
                ('occurrence', models.CharField(max_length=10, verbose_name=b'changes monthly or yearly', choices=[(b'monthly', b'Monthly'), (b'yearly', b'Yearly'), (b'none', b'None')])),
                ('count', models.CharField(max_length=20, verbose_name=b'Number of Leaves')),
                ('carry_forward', models.CharField(max_length=10, verbose_name=b'carry forward choices', choices=[(b'monthly', b'Monthly'), (b'yearly', b'Yearly'), (b'none', b'None')])),
                ('effective_from', models.DateField(verbose_name=b'date of effect')),
                ('apply_within_days', models.CharField(max_length=10, verbose_name=b'days limit for applying')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='leavesummary',
            name='leave_type',
            field=models.ForeignKey(verbose_name=b'Leave Type', to='Leave.LeaveType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leavesummary',
            name='user',
            field=models.ForeignKey(verbose_name=b'User', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='leavesummary',
            unique_together=set([('user', 'leave_type')]),
        ),
        migrations.AddField(
            model_name='leaveapplications',
            name='leave_type',
            field=models.ForeignKey(verbose_name=b'Leave Type', to='Leave.LeaveType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaveapplications',
            name='status_action_by',
            field=models.ForeignKey(related_name='applied_by', verbose_name=b'Change By User', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaveapplications',
            name='user',
            field=models.ForeignKey(related_name='user', verbose_name=b'User', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
