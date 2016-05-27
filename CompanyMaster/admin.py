from django.contrib import admin
from CompanyMaster.models import OfficeLocation, CustomerType,\
    DataPoint, Division, BusinessUnit, Holiday, Customer, Training, HRActivity


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


admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerType, CustomerTypeAdmin)
admin.site.register(Holiday, HolidayAdmin)
admin.site.register(HRActivity, HRActivityAdmin)
admin.site.register(BusinessUnit, BusinessUnitAdmin)
admin.site.register(OfficeLocation, OfficeLocatonAdmin)
admin.site.register(DataPoint, DataPointsAdmin)
admin.site.register(Training, TrainingAdmin)
