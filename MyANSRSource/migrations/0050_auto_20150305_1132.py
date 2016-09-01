# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('MyANSRSource', '0049_auto_20150302_1430'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project', models.ForeignKey(to='MyANSRSource.Project')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='project',
            name='pm',
            field=models.ManyToManyField(related_name='New Project Manager', verbose_name=b'New Project Leader', through='MyANSRSource.ProjectManager', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
