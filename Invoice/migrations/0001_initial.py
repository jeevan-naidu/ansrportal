# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-03-31 13:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('MyANSRSource', '0111_auto_20170116_1651'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(default=b'submitter', max_length=30, verbose_name=b'role')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Creation Date')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name=b'Last Updated')),
                ('is_active', models.BooleanField(default=True, verbose_name=b'Is Active')),
                ('process_status', models.CharField(choices=[(b'Not Started', b'Not Started'), (b'In Progress', b'In Progress'), (b'Rolled Back', b'Rolled Back'), (b'Completed', b'Completed')], default=b'In Progress', max_length=40)),
                ('request_status', models.CharField(choices=[(b'Initiated', b'Initiated'), (b'Withdrawn', b'Withdrawn'), (b'Completed', b'Completed')], default=b'Initiated', max_length=40)),
                ('milestone_date', models.DateField()),
                ('milestone_name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('closed_on_date', models.DateField()),
                ('amount', models.IntegerField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MyANSRSource.Project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoice_requested_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(default=b'submitter', max_length=30, verbose_name=b'role')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Creation Date')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name=b'Last Updated')),
                ('status', models.CharField(choices=[(b'approve', b'Approve'), (b'reject', b'Reject')], max_length=20)),
                ('reason', models.TextField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction_approved_by', to=settings.AUTH_USER_MODEL)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Invoice.Invoice')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
