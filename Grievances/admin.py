from django.contrib import admin
from models import Grievances, Grievances_category
# Register your models here.

class GrievancesAdmin(admin.ModelAdmin):
    list_display = ['grievance_id', 'user', 'category', 'subject', 'grievance', 'escalate', 'active', 'created_date' ]
    list_filter = ('user', 'category', 'active','created_date')
    
admin.site.register(Grievances, GrievancesAdmin)
admin.site.register(Grievances_category)

