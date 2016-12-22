# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-12-08 09:09
from __future__ import unicode_literals

import Leave.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaveApplications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_date', models.DateField(verbose_name=b'Leave from Date')),
                ('from_session', models.CharField(choices=[(b'session_first', b'First Half'), (b'session_second', b'Second Half')], max_length=20, verbose_name=b'')),
                ('to_date', models.DateField(verbose_name=b'Leave to Date')),
                ('to_session', models.CharField(choices=[(b'session_first', b'First Half'), (b'session_second', b'Second Half')], max_length=20, verbose_name=b'')),
                ('reason', models.CharField(blank=True, max_length=1000, null=True, verbose_name=b'Reason')),
                ('status', models.CharField(choices=[(b'open', b'Open'), (b'approved', b'Approved'), (b'rejected', b'Rejected'), (b'cancelled', b'Cancelled')], max_length=100, verbose_name=b'Status Of Leave')),
                ('status_action_on', models.DateField(auto_now=True, verbose_name=b'Date of Change')),
                ('status_comments', models.CharField(max_length=500, verbose_name=b'Status change comment')),
                ('due_date', models.DateField(null=True, verbose_name=b'application of comp off')),
                ('days_count', models.CharField(max_length=10, verbose_name=b'Leave Count')),
                ('atachement', models.FileField(blank=True, null=True, upload_to=Leave.models.content_file_name, verbose_name=b'Attachment')),
                ('applied_on', models.DateField(auto_now_add=True, verbose_name=b'Leave Applied Date')),
                ('modified_on', models.DateField(auto_now=True, verbose_name=b'Modified Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
                ('applied_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='applied_by_user', to=settings.AUTH_USER_MODEL, verbose_name=b'Leaved applied by ')),
                ('apply_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='manager', to=settings.AUTH_USER_MODEL, verbose_name=b'Manager')),
            ],
        ),
        migrations.CreateModel(
            name='LeaveSummary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=10, verbose_name=b'Current Year')),
                ('applied', models.CharField(max_length=20, verbose_name=b'applied leave count')),
                ('approved', models.CharField(max_length=20, verbose_name=b'approved leave count')),
                ('balance', models.CharField(max_length=20, verbose_name=b'balance leave count')),
            ],
        ),
        migrations.CreateModel(
            name='LeaveType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leave_type', models.CharField(choices=[(b'earned_leave', b'Earned Leave'), (b'sick_leave', b'Sick Leave'), (b'casual_leave', b'Casual Leave'), (b'short_leave', b'Short Leave'), (b'loss_of_pay', b'Loss Of Pay'), (b'bereavement_leave', b'Bereavement Leave'), (b'maternity_leave', b'Maternity Leave'), (b'paternity_leave', b'Paternity Leave'), (b'comp_off_earned', b'Comp Off Earned'), (b'comp_off_avail', b'Comp Off Avail'), (b'pay_off', b'Pay Off'), (b'work_from_home', b'Work From Home'), (b'sabbatical', b'Sabbatical')], max_length=50, verbose_name=b'Leave Types')),
                ('occurrence', models.CharField(choices=[(b'monthly', b'Monthly'), (b'yearly', b'Yearly'), (b'none', b'None')], max_length=10, verbose_name=b'changes monthly or yearly')),
                ('count', models.CharField(max_length=20, verbose_name=b'Number of Leaves')),
                ('carry_forward', models.CharField(choices=[(b'monthly', b'Monthly'), (b'yearly', b'Yearly'), (b'none', b'None')], max_length=10, verbose_name=b'carry forward choices')),
                ('effective_from', models.DateField(verbose_name=b'date of effect')),
                ('apply_within_days', models.CharField(max_length=10, verbose_name=b'days limit for applying')),
            ],
        ),
        migrations.CreateModel(
            name='ShortAttendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_leave_type', models.CharField(choices=[(b'half_day', b'HALF DAY'), (b'full_day', b'FULL DAY')], max_length=50, verbose_name=b'leave type')),
                ('for_date', models.DateField(verbose_name=b'short attendance applied for date')),
                ('stay_time', models.TimeField(blank=True, null=True, verbose_name=b'stay time with in office')),
                ('status', models.CharField(choices=[(b'open', b'Open'), (b'closed', b'Closed'), (b'accepted', b'Accepted')], max_length=100, verbose_name=b'Status Of Short attendance')),
                ('status_action_on', models.DateField(auto_now=True, verbose_name=b'Status Change date')),
                ('status_comments', models.CharField(max_length=500, verbose_name=b'Status change comment')),
                ('dispute', models.CharField(choices=[(b'open', b'Open'), (b'raised', b'Raised'), (b'approved', b'Approved'), (b'rejected', b'Rejected')], max_length=100, verbose_name=b'Status Of Dispute')),
                ('due_date', models.DateField(null=True, verbose_name=b'date before resolve short attendance')),
                ('reason', models.CharField(blank=True, max_length=1000, null=True, verbose_name=b'Reason')),
                ('applied_on', models.DateField(auto_now_add=True, verbose_name=b'short attendance Applied Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
                ('swipe_in', models.TimeField(blank=True, null=True, verbose_name=b'swipe in time')),
                ('swipe_out', models.TimeField(blank=True, null=True, verbose_name=b'swipe out time')),
                ('apply_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Smanager', to=settings.AUTH_USER_MODEL, verbose_name=b'Manager')),
                ('status_action_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_taker', to=settings.AUTH_USER_MODEL, verbose_name=b'action taken By User')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applied_for_user', to=settings.AUTH_USER_MODEL, verbose_name=b'User')),
            ],
        ),
        migrations.AddField(
            model_name='leavesummary',
            name='leave_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Leave.LeaveType', verbose_name=b'Leave Type'),
        ),
        migrations.AddField(
            model_name='leavesummary',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name=b'User'),
        ),
        migrations.AddField(
            model_name='leaveapplications',
            name='leave_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Leave.LeaveType', verbose_name=b'Leave Type'),
        ),
        migrations.AddField(
            model_name='leaveapplications',
            name='status_action_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_by', to=settings.AUTH_USER_MODEL, verbose_name=b'Change By User'),
        ),
        migrations.AddField(
            model_name='leaveapplications',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL, verbose_name=b'User'),
        ),
    ]
