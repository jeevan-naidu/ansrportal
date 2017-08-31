from django.contrib import admin
from models import SalesforceData
# Register your models here.

class SalesforceDataAdmin(admin.ModelAdmin):
    list_display = ('opportunity_number', 'opportunity_name', 'customer_contact', 'account_name',
                    'value','planned_start_date', 'planned_end_date')
    list_filter = ('opportunity_number', 'customer_contact')
    search_fields = ['opportunity_number','opportunity_name']
admin.site.register(SalesforceData, SalesforceDataAdmin)
