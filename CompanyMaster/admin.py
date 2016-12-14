from django.contrib import admin
from django.contrib.auth.models import User
from CompanyMaster.models import OfficeLocation, CustomerType,\
    DataPoint, Division, BusinessUnit, Holiday, Customer, Training, HRActivity,\
    Country, Currency, Region, Company, CustomerGroup, Department, PnL, Practice,\
    SubPractice, CareerBand, Role, Designation, KRA
from forms import UserChoiceField


class DivisionInline(admin.TabularInline):
    model = Division
    extra = 1
    ordering = ['name', ]


class OfficeLocatonAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state',)


class CustomerTypeAdmin(admin.ModelAdmin):
    list_display = ('name', )


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'customerCode', 'customergroup')


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [DivisionInline, ]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'head':
            kwargs["queryset"] = User.objects.filter(is_active=True).order_by('first_name')
            kwargs['form_class'] = UserChoiceField
        return super(DepartmentAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class BusinessUnitAdmin(admin.ModelAdmin):
    list_display = ('name',)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'new_bu_head':
            kwargs["queryset"] = User.objects.filter(is_active=True).order_by('first_name')
            kwargs['form_class'] = UserChoiceField
        return super(BusinessUnitAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', )


class HRActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', )


class TrainingAdmin(admin.ModelAdmin):
    list_display = ('batch', 'trainingDate', 'endDate')

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'trainer':
            kwargs["queryset"] = User.objects.filter(is_active=True).order_by('first_name')
            kwargs['form_class'] = UserChoiceField
        return super(TrainingAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class DataPointsAdmin(admin.ModelAdmin):
    list_display = ('name', )

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'lead':
            kwargs["queryset"] = User.objects.filter(is_active=True).order_by('first_name')
            kwargs['form_class'] = UserChoiceField
        return super(DataPointsAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class CountryAdmin(admin.ModelAdmin):
    list_display = ('country_code', 'country_name', 'region_code', 'privacy_rule', 'currency_code', 'is_active')


class CurrencyAdmin(admin.ModelAdmin):
    fields = ['currency_code', 'currency_name', 'default', 'is_active']
    list_display = ('currency_code', 'currency_name', 'default', 'is_active')


class RegionAdmin(admin.ModelAdmin):
    fields = ['region_code', 'region_name', 'is_active']
    list_display = ('region_code', 'region_name', 'is_active')

    def save_model(self, request, obj, form, change):
        region_code = obj.region_code
        obj.user = request.user
        region = Region.objects.filter(region_code=region_code)
        if region:
            obj.updatedby = obj.user.id
        else:
            obj.createdby = obj.user.id
            obj.updatedby = obj.user.id

        super(RegionAdmin, self).save_model(request, obj, form, change)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_legal_name', 'country', 'legal_HQ_address', 'legal_HQ_city',
                    'legal_HQ_state', 'legal_HQ_zipcode')


class CustomerGroupAdmin(admin.ModelAdmin):
    list_display = ('customer_group_code', 'customer_group_name', 'is_active')


class PnLAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'owner', 'is_active')

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'owner':
            kwargs["queryset"] = User.objects.filter(is_active=True).order_by('first_name')
            kwargs['form_class'] = UserChoiceField
        return super(PnLAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class RoleAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active')


class PracticeAdmin(admin.ModelAdmin):
    fields = ['code', 'name', 'department', 'head', 'sub_practice', 'is_active']
    list_display = ('code', 'name', 'department', 'head', 'sub_practice', 'is_active')

    def save_model(self, request, obj, form, change):
        code = obj.code
        obj.user = request.user
        practice = Practice.objects.filter(code=code)
        if practice:
            obj.updatedby = obj.user.id
        else:
            obj.createdby = obj.user.id
            obj.updatedby = obj.user.id

        super(PracticeAdmin, self).save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'department':
            kwargs["queryset"] = Department.objects.filter(practices=True)
        if db_field.name == 'head':
            kwargs["queryset"] = User.objects.filter(is_active=True).order_by('first_name')
            kwargs['form_class'] = UserChoiceField
        return super(PracticeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)



class DesignationAdmin(admin.ModelAdmin):
    fields = ['name', 'role', 'career_band_code', 'steps', 'is_active']
    list_display = ('name', 'role', 'career_band_code', 'steps', 'is_active')

    def save_model(self, request, obj, form, change):
        name = obj.name
        obj.user = request.user
        designation = Designation.objects.filter(name=name)
        if designation:
            obj.updatedby = obj.user.id
        else:
            obj.createdby = obj.user.id
            obj.updatedby = obj.user.id

        super(DesignationAdmin, self).save_model(request, obj, form, change)


class KRAAdmin(admin.ModelAdmin):
    fields = ['designation', 'series', 'narration', 'is_active']
    list_display = ('designation', 'series', 'narration', 'is_active')

    def save_model(self, request, obj, form, change):
        designation = obj.designation
        obj.user = request.user
        series = obj.series
        kra = KRA.objects.filter(designation=designation, series=series)
        if kra:
            obj.updatedby = obj.user.id
        else:
            obj.createdby = obj.user.id
            obj.updatedby = obj.user.id

        super(KRAAdmin, self).save_model(request, obj, form, change)


class CareerBandAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'is_active')


class SubPracticeAdmin(admin.ModelAdmin):
    fields = ['code', 'name', 'practice', 'is_active',]
    list_display = ('code', 'name', 'practice', 'is_active')

    def save_model(self, request, obj, form, change):
        code = obj.code
        obj.user = request.user
        sub_practice = SubPractice.objects.filter(code=code)
        if sub_practice:
            obj.updatedby = obj.user.id
        else:
            obj.createdby = obj.user.id
            obj.updatedby = obj.user.id

        super(SubPracticeAdmin, self).save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'practice':
            kwargs["queryset"] = Practice.objects.filter(sub_practice=True)
        return super(SubPracticeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class DepartmentAdmin(admin.ModelAdmin):
    fields = ['name', 'code', 'head', 'billable', 'practices', 'is_active']
    list_display = ('name', 'code', 'head', 'billable', 'practices', 'is_active')

    def save_model(self, request, obj, form, change):
        code = obj.code
        user = obj.user = request.user
        department = Department.objects.filter(code=code)
        if department:
            obj.updatedby = user.id
        else:
            obj.createdby = user.id
            obj.updatedby = user.id

        super(DepartmentAdmin, self).save_model(request, obj, form, change)

admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerType, CustomerTypeAdmin)
admin.site.register(Holiday, HolidayAdmin)
admin.site.register(HRActivity, HRActivityAdmin)
admin.site.register(BusinessUnit, BusinessUnitAdmin)
admin.site.register(OfficeLocation, OfficeLocatonAdmin)
admin.site.register(DataPoint, DataPointsAdmin)
admin.site.register(Training, TrainingAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(CustomerGroup, CustomerGroupAdmin)
admin.site.register(PnL, PnLAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Practice, PracticeAdmin)
admin.site.register(Designation, DesignationAdmin)
admin.site.register(KRA, KRAAdmin)
admin.site.register(CareerBand, CareerBandAdmin)
admin.site.register(SubPractice, SubPracticeAdmin)
admin.site.register(Department, DepartmentAdmin)



