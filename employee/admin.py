from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin

from employee.models import Employee, PreviousEmployment, EmpAddress,\
    FamilyMember, Education, Designation, TeamMember, Attendance


class EmpAddressInline(admin.StackedInline):
    model = EmpAddress
    extra = 1
    inline_classes = ('grp-collapse grp-open',)
    fields = ('address_type', 'address1', 'address2',
              ('city', 'state', 'zipcode'))

    verbose_name = 'Address'
    verbose_name = 'Addresses'

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            # Don't add any extra forms if
            # the related object already
            # exists.
            return 0
        return self.extra


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1
    classes = ('grp-collapse grp-open',)

    verbose_name = 'Qualification'
    verbose_name_plural = 'Qualifications'

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            # Don't add any extra forms if
            # the related object already
            # exists.
            return 0
        return self.extra


class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 1
    classes = ('grp-collapse grp-open',)

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            # Don't add any extra forms if
            # the related object already
            # exists.
            return 0
        return self.extra


class PreviousEmploymentInline(admin.StackedInline):
    model = PreviousEmployment
    extra = 1
    classes = ('grp-collapse grp-open',)
    inline_classes = ('grp-collapse grp-open',)

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            # Don't add any extra forms if
            # the related object already
            # exists.
            return 0
        return self.extra


class UserInline(admin.StackedInline):
    extra = 0
    verbose_name = 'Click to open/close...'
    verbose_name_plural = 'Employee Information'
    model = Employee
    can_delete = False
    # Grappelli stylesheets
    classes = ('grp-collapse grp-open',)
    inline_classes = ('grp-collapse grp-closed',)

    max_num = 1
    min_num = 1

    fieldsets = (
        ('Manager Information', {
            'fields': ('manager', 'is_360eligible', ),
        }),
        ('Employee Identification', {
            'fields': (('middle_name',),
                       ('date_of_birthO', 'gender', 'nationality'),
                       'date_of_birthR',
                       ('marital_status', 'wedding_date', 'blood_group'),
                       'exprience'), }),
        ('Contact Details', {
            'fields': (
                ('mobile_phone', 'land_phone',
                 'emergency_phone'), 'personal_email',)}),
        ('Role and Job', {
            'fields': (('employee_assigned_id', 'designation'),
                       ('business_unit', 'location'),
                       ('category', 'idcard'),)}),
        ('Financial Information', {
            'fields': (('PAN', 'PF_number', 'uan'),
                       ('group_insurance_number', 'esi_number',),
                       )}),
        ('Key Dates', {
            'fields': (('joined', 'confirmation', 'last_promotion'),
                       ('resignation', 'exit',)), }, ),
    )

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            # Don't add any extra forms if
            # the related object already
            # exists.
            return 0
        return self.extra


class EmployeeAdmin(OriginalUserAdmin):
    readonly_fields = ('email', )
    inlines = [UserInline, EmpAddressInline, EducationInline,
               FamilyMemberInline,
               PreviousEmploymentInline, ]
    max_num = 1
    min_num = 1

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

    add_fieldsets = (
        ('Add', {'fields': ('username', 'password1', 'password2'), }, ),
    )

    def get_fieldsets(self, request, obj=None, **kwargs):
        if obj is None:
            return self.add_fieldsets

        if request.user.is_superuser:
            return self.super_fieldsets
        else:
            return self.ord_fieldsets

    def get_queryset(self, request):
        qs = super(OriginalUserAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            # If you are an user with is_staff = True we still wont allow
            # you to see superuser's records.
            qs = qs.exclude(is_superuser=True)
            return qs


class DesignationAdmin(admin.ModelAdmin):
    pass
#    def get_queryset(self, request):
#        return self.get_queryset(request).filter(active=True)


class AttendanceAdmin(admin.ModelAdmin):
    readonly_fields = (
        'employee',
        'incoming_employee_id',
        'swipe_in',
        'swipe_out')
    list_display = (
        'attdate',
        'employee',
        'incoming_employee_id',
        'swipe_in',
        'swipe_out',
        )
    list_filter = ('employee', 'incoming_employee_id', 'attdate',)
    ordering = ('attdate', 'employee',)
    date_hierarchy = 'attdate'

admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(TeamMember, EmployeeAdmin)
admin.site.register(Designation, DesignationAdmin)
