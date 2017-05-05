# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-04-11 09:55
from __future__ import unicode_literals

import Grievances.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Grievances',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grievance_id', models.CharField(max_length=60, unique=True)),
                ('subject', models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(15)])),
                ('grievance', models.TextField(help_text=b"<span id='textarea_remaining'>2000 remaining</span>", max_length=2200, validators=[django.core.validators.MinLengthValidator(15)])),
                ('action_taken', models.TextField(blank=True, max_length=2000, null=True, validators=[django.core.validators.MinLengthValidator(15)])),
                ('user_closure_message', models.TextField(blank=True, max_length=2000, null=True, validators=[django.core.validators.MinLengthValidator(5)])),
                ('admin_closure_message', models.TextField(blank=True, max_length=2000, null=True, validators=[django.core.validators.MinLengthValidator(5)])),
                ('satisfaction_level', models.CharField(blank=True, choices=[(b'satisfied', b'Satisfied'), (b'not_sure', b'Not Sure'), (b'dissatisfied', b'Dissatisfied'), (b'very_dissatisfied', b'Very Dissatisfied')], max_length=50, null=True)),
                ('escalate', models.BooleanField(default=False)),
                ('escalate_to', models.CharField(blank=True, help_text=b"In case of multiple email id's, seperate them by a semicolan. Do not use single or double quotes anywhere", max_length=200, null=True)),
                ('grievance_attachment', models.FileField(blank=True, null=True, upload_to=Grievances.models.change_file_path)),
                ('admin_action_attachment', models.FileField(blank=True, null=True, upload_to=Grievances.models.change_file_path)),
                ('user_closure_message_attachment', models.FileField(blank=True, null=True, upload_to=Grievances.models.change_file_path)),
                ('admin_closure_message_attachment', models.FileField(blank=True, null=True, upload_to=Grievances.models.change_file_path)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('action_taken_date', models.DateTimeField(blank=True, null=True)),
                ('admin_closure_message_date', models.DateTimeField(blank=True, null=True)),
                ('closure_date', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
                ('grievance_status', models.CharField(choices=[(b'new', b'New'), (b'opened', b'Open'), (b'in_progress', b'In Progress'), (b'closed', b'Closed')], default=b'new', max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Grievances',
            },
        ),
        migrations.CreateModel(
            name='Grievances_category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=200)),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
            ],
        ),
        migrations.AddField(
            model_name='grievances',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grievances.Grievances_category'),
        ),
        migrations.AddField(
            model_name='grievances',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
