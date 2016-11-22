from django.contrib import admin
from CompanyMaster.models import OfficeLocation, CustomerType,\
    DataPoint, Division, BusinessUnit, Holiday, Customer, Training, HRActivity,\
    Country, Currency, Region, Company, CustomerGroup


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

