from django.contrib import admin
from CompanyMaster.models import OfficeLocation, CustomerType,\
    DataPoint, Division, BusinessUnit, Holiday, Customer, Training, HRActivity,\
    Country, Currency, Region, Company, CustomerGroup, Department, PnL, Practice,\
    SubPractice, CareerBand, Role, Designation, KRA


class DivisionInline(admin.TabularInline):
    model = Division
    extra = 1
    ordering = ['name', ]


class OfficeLocatonAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state',)


class CustomerTypeAdmin(admin.ModelAdmin):
    list_display = ('name', )


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'customerCode')


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [DivisionInline, ]


class BusinessUnitAdmin(admin.ModelAdmin):
    list_display = ('name',)


class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', )


class HRActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', )


class TrainingAdmin(admin.ModelAdmin):
    list_display = ('batch', 'trainingDate', 'endDate')


class DataPointsAdmin(admin.ModelAdmin):
    list_display = ('name', )


class CountryAdmin(admin.ModelAdmin):
    list_display = ('country_code', 'country_name', 'region_code', 'privacy_rule', 'currency_code', 'is_active')


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('currency_code', 'currency_name', 'default', 'is_active')


class RegionAdmin(admin.ModelAdmin):
    list_display = ('region_code', 'region_name', 'is_active')


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_legal_name', 'country', 'legal_HQ_address', 'legal_HQ_city',
                    'legal_HQ_state', 'legal_HQ_zipcode')


class CustomerGroupAdmin(admin.ModelAdmin):
    list_display = ('customer_group_code', 'customer_group_name', 'is_active')


class PnLAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'owner', 'is_active')


class RoleAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active')


class PracticeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'head', 'sub_practice', 'is_active')


class DesignationAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'career_band_code', 'is_active')


class KRAAdmin(admin.ModelAdmin):
    list_display = ('designation', 'series', 'narration', 'is_active')


class CareerBandAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'is_active')


class SubPracticeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'practice', 'is_active')


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'head', 'billable', 'practices', 'is_active')

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



