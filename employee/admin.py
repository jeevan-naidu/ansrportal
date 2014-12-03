from django.contrib import admin
from employee.models import Employee, PreviousEmployment, EmpAddress, FamilyMember, Education
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin

# Register your models here.

class PreviousEmploymentInline(admin.TabularInline):
    model = PreviousEmployment

class UserInline(admin.StackedInline):
    model = Employee
    can_delete = False

    fieldsets = (
        ('Employee Identification', {
            'fields': (
                'middle_name', 'employee_assigned_id')}),
        ('Contact Details', {
            'fields': (
                'permanent_address', 'temporary_address', 'mobile_phone',
                'land_phone', 'emergency_phone', 'personal_email',)}),
        ('Other Details', {
            'fields': (
                'date_of_birth', 'gender', 'nationality',
                'marital_status', 'blood_group',)}),
        ('Role and Job', {
            'fields': ('employee_assigned_id', 'designation',
                'division', 'location', 'category', 'idcard',)}),
        ('Financial Information', {
            'fields': ('PAN', 'PF_number',
                'bank_name', 'bank_branch', 'bank_account', 'bank_ifsc_code',
                       'group_insurance_number', 'esi_number',
                       )}),
        ('Key Dates', {
            'fields': ('joined', 'confirmation', 'last_promotion',
                       'resignation', 'exit',), }, ),
    )


class EmployeeAdmin(OriginalUserAdmin):
    inlines = [UserInline,PreviousEmploymentInline,  ]


try:
    admin.site.unregister(User)
finally:
    admin.site.register(User, EmployeeAdmin)

#admin.site.register(Employee, EmployeeAdmin)
