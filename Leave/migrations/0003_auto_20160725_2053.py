# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Leave', '0002_auto_20160713_2132'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaveapplications',
            name='applied_by',
            field=models.ForeignKey(related_name='applied_by_user', verbose_name=b'Leaved applied by ', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='leaveapplications',
            name='status_action_by',
            field=models.ForeignKey(related_name='action_by', verbose_name=b'Change By User', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
