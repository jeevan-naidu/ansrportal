# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import Grievances.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Grievances',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('grievance_id', models.CharField(unique=True, max_length=60)),
                ('subject', models.CharField(max_length=100)),
                ('grievance', models.TextField(max_length=2000)),
                ('action_taken', models.TextField(max_length=2000, null=True, blank=True)),
                ('user_closure_message', models.TextField(max_length=2000, null=True, blank=True)),
                ('admin_closure_message', models.TextField(max_length=2000, null=True, blank=True)),
                ('satisfaction_level', models.CharField(blank=True, max_length=50, null=True, choices=[(b'satisfied', b'Satisfied'), (b'not_sure', b'Not Sure'), (b'dissatisfied', b'Dissatisfied'), (b'very_dissatisfied', b'Very Dissatisfied')])),
                ('escalate', models.BooleanField(default=False)),
                ('escalate_to', models.CharField(help_text=b"In case of multiple email id's, seperate them by a semicolan. Do not use single or double quotes anywhere", max_length=200, null=True, blank=True)),
                ('grievance_attachment', models.FileField(null=True, upload_to=Grievances.models.change_file_path, blank=True)),
                ('admin_action_attachment', models.FileField(null=True, upload_to=Grievances.models.change_file_path, blank=True)),
                ('user_closure_message_attachment', models.FileField(null=True, upload_to=Grievances.models.change_file_path, blank=True)),
                ('admin_closure_message_attachment', models.FileField(null=True, upload_to=Grievances.models.change_file_path, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('action_taken_date', models.DateTimeField(null=True, blank=True)),
                ('admin_closure_message_date', models.DateTimeField(null=True, blank=True)),
                ('closure_date', models.DateTimeField(null=True, blank=True)),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
            ],
            options={
                'verbose_name_plural': 'Grievances',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Grievances_catagory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('catagory', models.CharField(max_length=200)),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='grievances',
            name='catagory',
            field=models.ForeignKey(to='Grievances.Grievances_catagory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='grievances',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
