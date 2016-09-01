# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('Grievances', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Grievances_catagory',
            new_name='Grievances_category',
        ),
        migrations.RenameField(
            model_name='grievances',
            old_name='catagory',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='grievances_category',
            old_name='catagory',
            new_name='category',
        ),
        migrations.AddField(
            model_name='grievances',
            name='grievance_status',
            field=models.CharField(default=b'new', max_length=50, choices=[(b'new', b'New'), (b'opened', b'Open'), (b'in_progress', b'In Progress'), (b'closed', b'Closed')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='grievances',
            name='action_taken',
            field=models.TextField(blank=True, max_length=2000, null=True, validators=[django.core.validators.MinLengthValidator(15)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='grievances',
            name='admin_closure_message',
            field=models.TextField(blank=True, max_length=2000, null=True, validators=[django.core.validators.MinLengthValidator(5)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='grievances',
            name='grievance',
            field=models.TextField(help_text=b"<span id='textarea_remaining'>2000 remaining</span>", max_length=2200, validators=[django.core.validators.MinLengthValidator(15)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='grievances',
            name='subject',
            field=models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(15)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='grievances',
            name='user_closure_message',
            field=models.TextField(blank=True, max_length=2000, null=True, validators=[django.core.validators.MinLengthValidator(5)]),
            preserve_default=True,
        ),
    ]
