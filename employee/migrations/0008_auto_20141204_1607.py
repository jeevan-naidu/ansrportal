# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('employee', '0007_auto_20141204_1150'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='permanent_address',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='temporary_address',
        ),
        migrations.AddField(
            model_name='empaddress',
            name='address_type',
            field=models.CharField(default=b'TM', max_length=2, verbose_name=b'Address Type', choices=[(b'PR', b'Permanent'), (b'TM', b'Temporary')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='empaddress',
            name='employee',
            field=models.ForeignKey(default=0, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
