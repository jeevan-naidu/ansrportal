from django.contrib import admin
from CompanyMaster.models import OfficeLocation,\
    Department, Division, BusinessUnit


class DivisionInline(admin.TabularInline):
    model = Division
    extra = 1
    ordering = ['name', ]


class OfficeLocatonAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state',)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [DivisionInline, ]


class BusinessUnitAdmin(admin.ModelAdmin):
    list_display = ('name',)

# Register your models here.

admin.site.register(Department, DepartmentAdmin)
admin.site.register(BusinessUnit, BusinessUnitAdmin)
admin.site.register(OfficeLocation, OfficeLocatonAdmin)
