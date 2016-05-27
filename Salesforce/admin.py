from django.contrib import admin
from models import SalesforceData
# Register your models here.

class SalesforceDataAdmin(admin.ModelAdmin):
    list_display = ('opportunity_number', 'opportunity_name', 'business_unit', 'customer_contact', 'account_name',
                    'value', 'probability', 'start_date', 'end_date', 'status')
    list_filter = ('opportunity_number', 'business_unit', 'customer_contact','status')
    
admin.site.register(SalesforceData, SalesforceDataAdmin)
