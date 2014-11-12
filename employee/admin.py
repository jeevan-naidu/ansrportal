from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from employee.models import *
# Register your models here.

class EmpBasicAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Employee Details',{
            'fields': ('first_name', 'middle_name', 'last_name', 'location_id', 
                       'gender', 'd_o_b', 'nationality', 'mar_sta', 'blood_grop',
                       'pan_no', 'passport_no', 'photo')
			    }),
	('Contact Details',{
            'fields': ('permanent_address', 'temporary_address', 'mob_num', 'land_num',
                       'emer_num', 'personal_email', 'official_email')
                           }),
	('Previous Employement Details',{
            'fields': ('prev_comp_name', 'prev_comp_addr', 'prev_comp_duration', 'prev_comp_pf',
                       'prev_comp_ctc', 'prev_leav_date')
                                        }),
        ('Employment Details',{
            'fields': ('emp_id', 'card_id', 'user_name', 'depar_code',
                       'cate_code', 'desig_code', 'year_exp', 'pf_no',
                       'join_date', 'prob_date', 'confirm_date', 'bus_route',
                       'busin_unit_code', 'cost_centre', 'group_insu_no', 'esi_num','emp_status', 'res_date', 'exit_date')
                              }),
	('Planning',{
            'fields': ('shift_plan', 'leave_plan', 'att_plan', 'over_tplan', 'lat_early_plan', 'off_day1', 'off_day2', 'apply_to')
                    }),
        ('Bank Details',{
            'fields': ('bank_name', 'bank_branch', 'bank_ac', 'ifsc_code')
                        }),
                 )


admin.site.register(EmpBasic, EmpBasicAdmin)
admin.site.register(EmpAddress)
admin.site.register(Education)
admin.site.register(Relative)
