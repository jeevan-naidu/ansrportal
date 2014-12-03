from django.contrib import admin
from employee.models import Employee
# Register your models here.


class EmployeeAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Employee Identification', {
            'fields': (
                'user.first_name', 'middle_name', 'user.last_name',
                'user.email',
                'employee_assigned_id')}),
        ('Contact Details', {
            'fields': (
                'permanent_address', 'temporary_address', 'mobile_phone',
                'land_phone', 'emergency_phone', 'personal_email',)}),
        ('Other Details', {
            'fields': (
                'date_of_birth', 'gender', 'nationality',
                'marital_status', 'blood_group',)}),
        ('Previous Employement', {
            'fields': (
                'previous_employment', ), }, ),
        ('Role and Job', {
            'fields': ('employee_assigned_id', 'designation',
                'division', 'location', 'category', 'idcard',)}),
        ('Financial Information', {
            'fields': ('PAN', 'PF_number',
                'bank_name', 'bank_branch', 'bank_account', 'ifsc_code',
                       'group_insurance_number', 'esi_number',
                       )}),
        ('Key Dates', {
            'fields': ('joined', 'confirmation', 'last_promotion',
                       'resignation', 'exit',), }, ),
    )


admin.site.register(Employee, EmployeeAdmin)
