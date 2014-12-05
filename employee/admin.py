from django.contrib import admin
from employee.models import Employee, PreviousEmployment, EmpAddress,\
    FamilyMember, Education, Designation, EmpAddress
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin


class EmpAddressInline(admin.TabularInline):
    model = EmpAddress

class EducationInline(admin.TabularInline):
    model = Education
    extra = 2

class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 2


class PreviousEmploymentInline(admin.StackedInline):
    model = PreviousEmployment
    extra = 1


class UserInline(admin.StackedInline):
    model = Employee
    can_delete = False

    fieldsets = (
        ('Employee Identification', {
            'fields': (
                'middle_name', 'employee_assigned_id')}),
        ('Contact Details', {
            'fields': (
                'mobile_phone', 'land_phone',
                'emergency_phone', 'personal_email',)}),
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

    inlines = [EmpAddressInline, ]

class EmployeeAdmin(OriginalUserAdmin):
    readonly_fields = ('email', )
    inlines = [UserInline, EducationInline, FamilyMemberInline, PreviousEmploymentInline, EmpAddressInline ]

class DesignationAdmin(admin.ModelAdmin):
    pass

try:
    admin.site.unregister(User)
finally:
    admin.site.register(User, EmployeeAdmin)

admin.site.register(Designation, DesignationAdmin)


#admin.site.register(Employee, EmployeeAdmin)
