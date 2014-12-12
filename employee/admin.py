from django.contrib import admin
from employee.models import Employee, PreviousEmployment, EmpAddress,\
    FamilyMember, Education, Designation
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin


class EmpAddressInline(admin.StackedInline):
    model = EmpAddress
    extra = 1
    fields = ('address_type', 'address1', 'address2',
              ('city', 'state', 'zipcode'))


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1
    classes = ('grp-collapse grp-closed',)


class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 1
    classes = ('grp-collapse grp-closed',)


class PreviousEmploymentInline(admin.StackedInline):
    model = PreviousEmployment
    extra = 1
    classes = ('grp-collapse grp-closed',)


class UserInline(admin.StackedInline):
    model = Employee
    can_delete = False
    # Grappelli stylesheets
    classes = ('grp-collapse grp-open',)
    inline_classes = ('grp-collapse grp-open',)

    fieldsets = (
        ('Employee Identification', {
            'fields': (
                'middle_name', )}),
        ('Contact Details', {
            'fields': (
                ('mobile_phone', 'land_phone',
                 'emergency_phone'), 'personal_email',)}),
        ('Other Details', {
            'fields': (
                ('date_of_birth', 'gender', 'nationality'),
                ('marital_status', 'blood_group'), 'exprience')}),
        ('Role and Job', {
            'fields': (('employee_assigned_id', 'designation'),
                       ('business_unit', 'division', 'location'),
                       ('category', 'idcard'),)}),
        ('Financial Information', {
            'fields': (('bank_name', 'bank_branch'),
                       ('bank_account', 'bank_ifsc_code',),
                       ('PAN', 'PF_number'),
                       ('group_insurance_number', 'esi_number',),
                       )}),
        ('Key Dates', {
            'fields': (('joined', 'confirmation', 'last_promotion'),
                       ('resignation', 'exit',)), }, ),
    )


class EmployeeAdmin(OriginalUserAdmin):
    readonly_fields = ('email', )
    inlines = [UserInline, EmpAddressInline, EducationInline,
               FamilyMemberInline,
               PreviousEmploymentInline, ]
#    exclude = ['groups', 'user_permissions', ]

    super_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        # ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    ord_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        # ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def get_fieldsets(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            return self.super_fieldsets
        else:
            return self.ord_fieldsets


class DesignationAdmin(admin.ModelAdmin):
    pass

try:
    admin.site.unregister(User)
finally:
    admin.site.register(User, EmployeeAdmin)

admin.site.register(Designation, DesignationAdmin)


#admin.site.register(Employee, EmployeeAdmin)
