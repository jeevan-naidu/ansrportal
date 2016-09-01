# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='education',
            name='nature_of_education',
            field=models.CharField(default=b'FT', max_length=2, verbose_name=b'Nature of Education', choices=[(b'FT', b'Full-time'), (b'PT', b'Part-time')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='education',
            name='specialization',
            field=models.CharField(max_length=30, null=True, verbose_name=b'Specialization', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='employee',
            name='wedding_date',
            field=models.DateField(null=True, verbose_name=b'Wedding Date', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='familymember',
            name='gender',
            field=models.CharField(default=b'M', max_length=1, verbose_name=b'Gender', choices=[(b'M', b'Male'), (b'F', b'Female')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='familymember',
            name='dob',
            field=models.DateField(null=True, verbose_name=b'DOB', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='familymember',
            name='rela_type',
            field=models.CharField(max_length=50, verbose_name=b'Relation Type', choices=[(b'FA', b'Father'), (b'MO', b'Mother'), (b'SP', b'Spouse'), (b'C1', b'Child1'), (b'C2', b'Child2'), (b'OO', b'Others')]),
            preserve_default=True,
        ),
    ]
