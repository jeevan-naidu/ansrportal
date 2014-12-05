# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('CompanyMaster', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Designation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40, verbose_name=b'Title')),
                ('billable', models.BooleanField(default=True, verbose_name=b'Billable')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'Degree')),
                ('from_date', models.DateField(verbose_name=b'From Date')),
                ('to_date', models.DateField(verbose_name=b'To Date')),
                ('institute', models.CharField(max_length=50, verbose_name=b'Institute Name')),
                ('overall_marks', models.IntegerField(max_length=50, verbose_name=b'Total Score/GPA')),
                ('employee', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Education',
                'verbose_name_plural': 'Education',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmpAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address_type', models.CharField(default=b'TM', max_length=2, verbose_name=b'Address Type', choices=[(b'PR', b'Permanent'), (b'TM', b'Temporary')])),
                ('address1', models.CharField(max_length=30, verbose_name=b'Address 1')),
                ('address2', models.CharField(max_length=30, verbose_name=b'Address 2')),
                ('city', models.CharField(max_length=15, verbose_name=b'City')),
                ('state', models.CharField(max_length=20, verbose_name=b'State')),
                ('zipcode', models.CharField(max_length=6, verbose_name=b'Zip Code')),
                ('employee', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Addresses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('status', models.BooleanField(default=True)),
                ('middle_name', models.CharField(max_length=15, verbose_name=b'Middle Name', blank=True)),
                ('gender', models.CharField(max_length=2, verbose_name=b'Gender', choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('date_of_birth', models.DateField(verbose_name=b'Date of Birth')),
                ('nationality', models.CharField(max_length=30, verbose_name=b'Nationality')),
                ('marital_status', models.CharField(max_length=10, verbose_name=b'Marital Status', choices=[(b'MA', b'Married'), (b'WD', b'Windowed'), (b'SE', b'Seperated'), (b'DV', b'Divorced'), (b'SG', b'Single')])),
                ('blood_group', models.CharField(blank=True, max_length=3, verbose_name=b'Blood Group', choices=[(b'00', b'A+'), (b'01', b'A-'), (b'02', b'B+'), (b'03', b'B-'), (b'04', b'O+'), (b'05', b'O-'), (b'06', b'AB+'), (b'07', b'AB-')])),
                ('mobile_phone', models.CharField(unique=True, max_length=15, verbose_name=b'Mobile Phone', blank=True)),
                ('land_phone', models.CharField(max_length=15, verbose_name=b'Landline Number', blank=True)),
                ('emergency_phone', models.CharField(unique=True, max_length=15, verbose_name=b'Emergency Contact Number')),
                ('personal_email', models.EmailField(unique=True, max_length=250, verbose_name=b'Personal E-mail')),
                ('passport_number', models.CharField(max_length=10, unique=True, null=True, verbose_name=b'Passport Number', blank=True)),
                ('photo', models.ImageField(upload_to=b'', storage=django.core.files.storage.FileSystemStorage(location=b'employee/emp_photo'), verbose_name=b'Employee Photo')),
                ('employee_assigned_id', models.CharField(max_length=15, serialize=False, verbose_name=b'Employee ID', primary_key=True)),
                ('idcard', models.CharField(unique=True, max_length=15, verbose_name=b'Access Card Number')),
                ('category', models.CharField(max_length=3, verbose_name=b'Employment Category', choices=[(b'FT', b'Fulltime Employee'), (b'PT', b'Parttime Employee'), (b'IN', b'Intern'), (b'CT', b'Contractor')])),
                ('exprience', models.IntegerField(max_length=3, verbose_name=b'Experience in Months')),
                ('joined', models.DateField(verbose_name=b'Joining Date')),
                ('confirmation', models.DateField(verbose_name=b'Confirmation Date')),
                ('last_promotion', models.DateField(verbose_name=b'Probation End Date')),
                ('resignation', models.DateField(null=True, verbose_name=b'Resignation Date', blank=True)),
                ('exit', models.DateField(null=True, verbose_name=b'Exit Date', blank=True)),
                ('PAN', models.CharField(unique=True, max_length=10, verbose_name=b'PAN Number')),
                ('PF_number', models.CharField(max_length=14, verbose_name=b'Provide Fund Number', blank=True)),
                ('bank_name', models.CharField(max_length=70, verbose_name=b'Bank Name')),
                ('bank_branch', models.CharField(max_length=70, verbose_name=b'Branch Name')),
                ('bank_account', models.IntegerField(unique=True, max_length=30, verbose_name=b'Account Number')),
                ('bank_ifsc_code', models.CharField(max_length=20, verbose_name=b'IFSC Code')),
                ('group_insurance_number', models.CharField(max_length=30, verbose_name=b'Group Insurance Number', blank=True)),
                ('esi_number', models.CharField(max_length=30, null=True, verbose_name=b'ESI Number', blank=True)),
                ('business_unit', models.ForeignKey(to='CompanyMaster.BusinessUnit')),
                ('designation', models.ForeignKey(to='employee.Designation')),
                ('division', models.ForeignKey(to='CompanyMaster.Division')),
                ('location', models.ForeignKey(to='CompanyMaster.OfficeLocation')),
                ('user', models.OneToOneField(verbose_name=b'User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FamilyMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'Name')),
                ('dob', models.DateField(verbose_name=b'DOB')),
                ('rela_type', models.CharField(max_length=50, verbose_name=b'Relation Type', choices=[(b'FA', b'Father'), (b'MO', b'Mother'), (b'SP', b'Spouse'), (b'C1', b'Child1'), (b'C2', b'Child2')])),
                ('employee', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PreviousEmployment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company_name', models.CharField(max_length=150, verbose_name=b'Company Name')),
                ('company_address', models.CharField(max_length=500, verbose_name=b'Company Address')),
                ('employed_from', models.DateField(verbose_name=b'Start Date')),
                ('employed_upto', models.DateField(verbose_name=b'End Date')),
                ('pf_number', models.CharField(max_length=15, null=True, verbose_name=b'PF Number', blank=True)),
                ('last_ctc', models.DecimalField(verbose_name=b'Last CTC', max_digits=15, decimal_places=2)),
                ('reason_for_exit', models.CharField(max_length=50, verbose_name=b'Reason for Exit')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name=b'created Date')),
                ('updatedon', models.DateTimeField(auto_now=True, verbose_name=b'Updated Date')),
                ('employee', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Previous Employment',
                'verbose_name_plural': 'Previous Employment',
            },
            bases=(models.Model,),
        ),
    ]
