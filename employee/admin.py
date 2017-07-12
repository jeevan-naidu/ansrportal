from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin
from employee.models import Employee, PreviousEmployment, EmpAddress,\
    FamilyMember, Education, Designation, TeamMember, Attendance, EmployeeCompanyInformation
from forms import EmployeeChoiceField, DesignationChoiceField
import CompanyMaster
from .forms import SetCurrentUserFormset


class SetCurrentUserFormsetMixin(object):
    """
    Use a generic formset which populates the 'created_by, updated_by' model field
    with the currently logged in user.
    """
    formset = SetCurrentUserFormset
    created_by = "created_by"
    updated_by = "updated_by"  # default user field name, override this to fit your model

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(SetCurrentUserFormsetMixin, self).get_formset(request, obj, **kwargs)
        formset.request = request
        formset.created_by = self.created_by
        formset.updated_by = self.updated_by
        return formset


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


class UserInline(SetCurrentUserFormsetMixin, admin.StackedInline):
    extra = 0
    verbose_name = 'Click to open/close...'
    verbose_name_plural = 'Employee Information'
    model = Employee
    can_delete = False
    # Grappelli stylesheets
    classes = ('grp-collapse grp-open',)
    inline_classes = ('grp-collapse grp-closed',)
    fk_name = "user"

    max_num = 1
    min_num = 1

    fieldsets = (
        ('Manager Information', {
            'fields': ('manager', ),
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
                       ('category', 'idcard', 'practice'),)}),
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
    list_display = (
        'username',
        'Employee_Id',
        'email',
        'last_name',
        'Joining_Date',
        'Exit_Date',
        'is_active',
        'is_staff',
    )

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

    def Employee_Id(self, user_obj):
        ''' Get employee id from Employee table'''

        try:
            emp_id = Employee.objects.get(user__email = user_obj.email).employee_assigned_id
        except:
            emp_id = None
        return emp_id

    def Joining_Date(self, user_obj):
        ''' Get employee joining date from Employee table'''

        try:
            emp_doj = Employee.objects.get(user__email=user_obj.email).joined
        except:
            emp_doj = None
        return emp_doj

    def Exit_Date(self, user_obj):
        ''' Get employee exit date from Employee table'''

        try:
            emp_exit_date = Employee.objects.get(user__email=user_obj.email).exit
        except:
            emp_exit_date = None
        return emp_exit_date


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


class EmployeeCompanyRelatedInformationAdmin(admin.ModelAdmin):
    fields = ['employee',  'company', 'pnl', 'designation', 'department', 'practice',
              'sub_practice', 'is_billable', 'billable_date']
    list_display = ('employee',  'company', 'pnl', 'designation', 'department',
                    'practice', 'sub_practice', 'is_billable', 'billable_date', )

    def save_model(self, request, obj, form, change):
        obj_id = obj.id
        user = obj.user = request.user
        department = EmployeeCompanyInformation.objects.filter(id=obj_id)
        if department:
            obj.updatedby = user.id
        else:
            obj.createdby = user.id
            obj.updatedby = user.id

        super(EmployeeCompanyRelatedInformationAdmin, self).save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'employee':
            kwargs["queryset"] = Employee.objects.filter(user__is_active=True).order_by('user__first_name')
            kwargs['form_class'] = EmployeeChoiceField
        if db_field.name == 'designation':
            kwargs["queryset"] = CompanyMaster.models.Designation.objects.filter(is_active=True).order_by('name')
            kwargs['form_class'] = DesignationChoiceField
        return super(EmployeeCompanyRelatedInformationAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(TeamMember, EmployeeAdmin)
admin.site.register(Designation, DesignationAdmin)
admin.site.register(EmployeeCompanyInformation, EmployeeCompanyRelatedInformationAdmin)
