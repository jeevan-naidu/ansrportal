# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MeetingRoomBooking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('from_time', models.DateTimeField()),
                ('to_time', models.DateTimeField()),
                ('status', models.CharField(max_length=100, choices=[(b'booked', b'Booked'), (b'cancelled', b'Cancelled')])),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name=b'last')),
                ('booked_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoomDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('room_name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100, choices=[(b'karle_ground_floor', b'Karle-Ground Floor'), (b'karle_second_floor', b'Karle-Second Floor'), (b'btp', b'BTP')])),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='meetingroombooking',
            name='room',
            field=models.ForeignKey(to='BookMyRoom.RoomDetail'),
            preserve_default=True,
        ),
    ]
