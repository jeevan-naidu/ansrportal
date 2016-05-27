# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyMaster', '0017_auto_20150415_0722'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='relatedMember',
        ),
    ]
