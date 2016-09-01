# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fb360', '0041_emppeer_survey'),
    ]

    operations = [
        migrations.CreateModel(
            name='Initiator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('employee', models.ForeignKey(related_name='emp', default=None, to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Respondent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'P', max_length=1, verbose_name=b'Status', choices=[(b'P', b'Pending'), (b'A', b'Approved'), (b'R', b'Rejected'), (b'D', b'Deleted')])),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('employee', models.ForeignKey(related_name='Pempl', default=None, verbose_name=b'Respondent', to=settings.AUTH_USER_MODEL)),
                ('initiator', models.ForeignKey(related_name='Pempl', default=None, verbose_name=b'Surve Initiator', to='fb360.Initiator')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='emppeer',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='emppeer',
            name='peer',
        ),
        migrations.RemoveField(
            model_name='emppeer',
            name='survey',
        ),
        migrations.AlterUniqueTogether(
            name='peer',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='peer',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='peer',
            name='emppeer',
        ),
        migrations.DeleteModel(
            name='EmpPeer',
        ),
        migrations.DeleteModel(
            name='Peer',
        ),
        migrations.AlterUniqueTogether(
            name='respondent',
            unique_together=set([('employee', 'initiator')]),
        ),
        migrations.AddField(
            model_name='initiator',
            name='respondents',
            field=models.ManyToManyField(default=None, related_name='Epeer', verbose_name=b'Choose Respondent', through='fb360.Respondent', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='initiator',
            name='survey',
            field=models.ForeignKey(default=None, to='fb360.FB360'),
            preserve_default=True,
        ),
    ]
