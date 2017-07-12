# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-07-12 05:37
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Invoice', '0004_auto_20170712_1101'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(default=b'submitter', max_length=30, verbose_name=b'role')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Creation Date')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name=b'Last Updated')),
                ('payment_status', models.CharField(choices=[(b'yes', b'Yes'), (b'no', b'No')], max_length=10)),
                ('payment_reason', models.TextField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_approved_by', to=settings.AUTH_USER_MODEL)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Invoice.Invoice')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
