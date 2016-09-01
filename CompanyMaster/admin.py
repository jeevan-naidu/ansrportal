from django.contrib import admin
from CompanyMaster.models import *


class DivisionInline(admin.TabularInline):
    model = Division
    extra = 1
    ordering = ['name', ]


class OfficeLocatonAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state',)


class CustomerTypeAdmin(admin.ModelAdmin):
    list_display = ('name', )


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_code')


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


admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerType, CustomerTypeAdmin)
admin.site.register(Holiday, HolidayAdmin)
admin.site.register(HRActivity, HRActivityAdmin)
admin.site.register(BusinessUnit, BusinessUnitAdmin)
admin.site.register(OfficeLocation, OfficeLocatonAdmin)
admin.site.register(DataPoint, DataPointsAdmin)
admin.site.register(Training, TrainingAdmin)

admin.site.register(Region)
admin.site.register(Currency)
admin.site.register(Country)
admin.site.register(Company)
admin.site.register(Location)
admin.site.register(SupportTask)
admin.site.register(Practice)
admin.site.register(SubPractice)
admin.site.register(Role)
admin.site.register(CareerBand)
admin.site.register(Designation)
admin.site.register(KRA)
admin.site.register(CareerLadderHeader)
admin.site.register(CareerLadder)
admin.site.register(PnL)
admin.site.register(BusinessSegment)
admin.site.register(GroupCustomer)
