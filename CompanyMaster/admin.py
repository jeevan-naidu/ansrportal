from django.contrib import admin
from CompanyMaster.models import OfficeLocation,\
    Department, Division, BusinessUnit, Holiday, Customer, Training


class DivisionInline(admin.TabularInline):
    model = Division
    extra = 1
    ordering = ['name', ]


class OfficeLocatonAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state',)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name','customerCode')


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [DivisionInline, ]


class BusinessUnitAdmin(admin.ModelAdmin):
    list_display = ('name',)


class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', )


class TrainingAdmin(admin.ModelAdmin):
    list_display = ('batch', 'trainingDate', )


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Holiday, HolidayAdmin)
# admin.site.register(Department, DepartmentAdmin)
admin.site.register(BusinessUnit, BusinessUnitAdmin)
admin.site.register(OfficeLocation, OfficeLocatonAdmin)
admin.site.register(Training, TrainingAdmin)
