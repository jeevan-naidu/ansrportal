from django.contrib import admin
from models import Grievances, Grievances_catagory
# Register your models here.

class GrievancesAdmin(admin.ModelAdmin):
    list_display = ['grievance_id', 'user', 'catagory', 'subject', 'grievance', 'escalate', 'active', 'created_date' ]
    list_filter = ('user', 'catagory', 'active','created_date')
    
admin.site.register(Grievances, GrievancesAdmin)
admin.site.register(Grievances_catagory)

