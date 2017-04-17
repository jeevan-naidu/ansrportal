from django.contrib import admin
from models import ResignationInfo, EmployeeClearanceInfo
from django.contrib.auth.models import User
# Register your models here.


class ClearanceInfoAdmin(admin.ModelAdmin):
    list_display = ['hr_clearance', 'IT_clearance', 'manager_clearance', 'admin_clearance', 'library_clearance']


class ResignationInfoAdmin(admin.ModelAdmin,):
    list_display = ['last_date', 'hr_accepted', 'emp_reason', 'manager_accepted', 'last_date_accepted',
                    'exit_interview_notes', 'exit_interview_flag', 'rehire_hr', 'rehire_manager', 'backup_taken']


class EmployeeClearanceInfoAdmin(admin.ModelAdmin):
    list_display = ['resignationInfo',  'department', 'dept_status', 'dept_feedback', 'dept_due']


admin.site.register(ResignationInfo, ResignationInfoAdmin)
admin.site.register(EmployeeClearanceInfo, EmployeeClearanceInfoAdmin)
