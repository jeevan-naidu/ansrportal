# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0026_auto_20151006_1216'),
        ('CompanyMaster', '0030_department_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessSegment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('segment_name', models.CharField(max_length=200, verbose_name=b'Segment Name')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CareerBand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('career_band_name', models.CharField(max_length=200, verbose_name=b'Career Band')),
                ('description', models.CharField(max_length=200, verbose_name=b'Description')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
            ],
            options={
                'verbose_name': 'Career Band',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CareerLadder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ladder_step', models.PositiveIntegerField(verbose_name=b'Ladder Step(Positive Integer)')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
            ],
            options={
                'verbose_name': 'Career Ladder Header',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CareerLadderHeader',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('career_ladder_header', models.CharField(max_length=200, verbose_name=b'Career Ladder Header')),
                ('description', models.CharField(max_length=500, verbose_name=b'Description')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
            ],
            options={
                'verbose_name': 'Career Ladder Header',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company_name', models.CharField(max_length=200, verbose_name=b'Company Name')),
                ('company_legal_name', models.CharField(max_length=200, verbose_name=b'Company Legal Name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('country_name', models.CharField(max_length=200, verbose_name=b'Country')),
                ('country_code', models.CharField(max_length=200, verbose_name=b'Country Code')),
                ('privacy_rule', models.CharField(max_length=200, verbose_name=b'Privacy Rule')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('currency_code', models.CharField(max_length=200, verbose_name=b'Currency Code')),
                ('currency_name', models.CharField(max_length=200, verbose_name=b'Currency Name')),
                ('default', models.CharField(max_length=200, verbose_name=b'Default')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomerNew',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('customer_code', models.CharField(max_length=200, verbose_name=b'Customer Code')),
                ('customer_name', models.CharField(max_length=200, verbose_name=b'Customer Name')),
                ('bill_to_email', models.EmailField(max_length=200, verbose_name=b'Bill To Email')),
                ('ship_to_email', models.EmailField(max_length=200, verbose_name=b'Ship To Email')),
                ('account_receivable_email', models.EmailField(max_length=200, verbose_name=b'Account Receivable Email')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Designation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('designation_name', models.CharField(max_length=200, verbose_name=b'Designation Name')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
                ('career_band_name', models.ForeignKey(verbose_name=b'Career Band Name', to='CompanyMaster.CareerBand')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KRA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('KRA_narration', models.CharField(max_length=1000, verbose_name=b'KRA Narration')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
                ('designation_name', models.ForeignKey(verbose_name=b'Designation', to='CompanyMaster.Designation')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location_name', models.CharField(max_length=200, verbose_name=b'Location Name')),
                ('street1', models.CharField(max_length=200, verbose_name=b'Street1')),
                ('street2', models.CharField(max_length=200, verbose_name=b'Street2')),
                ('street3', models.CharField(max_length=200, verbose_name=b'Street3')),
                ('city', models.CharField(max_length=200, verbose_name=b'City')),
                ('postal_code', models.CharField(max_length=6, verbose_name=b'ZIP or PIN code')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
                ('country', models.ForeignKey(verbose_name=b'Country', to='CompanyMaster.Country')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PnL',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pnl_name', models.CharField(max_length=200, verbose_name=b'PNL Name')),
                ('pnl_description', models.CharField(max_length=500, verbose_name=b'PNL Description')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Practice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('practice_name', models.CharField(max_length=200, verbose_name=b'Practice name')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
                ('department', models.ForeignKey(verbose_name=b'Department', to='CompanyMaster.Department')),
                ('practice_head', models.ForeignKey(verbose_name=b'Practice Head', to='employee.Employee')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('region_name', models.CharField(max_length=200, verbose_name=b'Region Name')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role_name', models.CharField(max_length=200, verbose_name=b'Role')),
                ('role_definition', models.CharField(max_length=1000, verbose_name=b'Role Definition')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubPractice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sub_practice_name', models.CharField(max_length=200, verbose_name=b'Sub Practice name')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
                ('pratice', models.ForeignKey(verbose_name=b'Practice Name', to='CompanyMaster.Practice')),
                ('sub_practice_lead', models.ForeignKey(verbose_name=b'Sub Practice Head', to='employee.Employee')),
            ],
            options={
                'verbose_name': 'Sub Practice',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SupportTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_name', models.CharField(max_length=100)),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('active', models.BooleanField(default=True, verbose_name=b'Is Active?')),
                ('department', models.ForeignKey(to='CompanyMaster.Department')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='designation',
            name='role',
            field=models.ManyToManyField(to='CompanyMaster.Role', verbose_name=b'Role'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customernew',
            name='HQ_address',
            field=models.ForeignKey(related_name='HQ Address', to='CompanyMaster.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customernew',
            name='account_delivery_manager',
            field=models.ForeignKey(related_name='Account Delivery Manager', to='employee.Employee'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customernew',
            name='account_relationship_manager',
            field=models.ForeignKey(related_name='Account Relationship Manager', to='employee.Employee'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customernew',
            name='bill_to_address',
            field=models.ForeignKey(related_name='Bill To Address', to='CompanyMaster.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customernew',
            name='business_segment',
            field=models.ForeignKey(related_name='Business Segment', to='CompanyMaster.BusinessSegment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customernew',
            name='ship_to_address',
            field=models.ForeignKey(related_name='Ship To Address', to='CompanyMaster.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='country',
            name='currency',
            field=models.ForeignKey(verbose_name=b'Currency Code', to='CompanyMaster.Currency'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='country',
            name='region_name',
            field=models.ForeignKey(verbose_name=b'Region Name', to='CompanyMaster.Region'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='company',
            name='HQ',
            field=models.ForeignKey(related_name='Head Quaters', to='CompanyMaster.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='company',
            name='locations',
            field=models.ManyToManyField(related_name='Locations', to='CompanyMaster.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='careerladder',
            name='career_ladder_header',
            field=models.ForeignKey(verbose_name=b'Career Ladder Header', to='CompanyMaster.CareerLadderHeader'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='careerladder',
            name='designation',
            field=models.ForeignKey(verbose_name=b'Designation', to='CompanyMaster.Designation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='businesssegment',
            name='pnl',
            field=models.ForeignKey(verbose_name=b'PNL Name', to='CompanyMaster.PnL'),
            preserve_default=True,
        ),
    ]
