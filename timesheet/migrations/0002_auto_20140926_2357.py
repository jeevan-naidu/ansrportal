# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='contigencyEffort',
        ),
        migrations.AddField(
            model_name='project',
            name='contingencyEffort',
            field=models.IntegerField(default=0, verbose_name=b'Contigency Effort'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='endDate',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'Project End Date'),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=50, verbose_name=b'Project Name'),
        ),
        migrations.AlterField(
            model_name='project',
            name='projectManager',
            field=models.ForeignKey(default=None, verbose_name=b'Project Manager', blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='project',
            name='startDate',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'Project Start Date'),
        ),
    ]
