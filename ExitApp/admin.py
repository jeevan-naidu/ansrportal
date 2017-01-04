from django.contrib import admin
from models import ResignationInfo, EmployeeClearanceInfo
from django.contrib.auth.models import User
# Register your models here.


class ClearanceInfoAdmin(admin.ModelAdmin):
    list_display = ['hr_clearance', 'IT_clearance', 'manager_clearance', 'admin_clearance', 'library_clearance']


class AcceptanceAdmin(admin.ModelAdmin,):
    list_display = ['last_date', 'hr_accepted', 'emp_reason', 'manager_accepted', 'last_date_accepted']


admin.site.register(ResignationInfo, AcceptanceAdmin)
