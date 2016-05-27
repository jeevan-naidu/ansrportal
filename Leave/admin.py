from django.contrib import admin
from models import LeaveType, LeaveSummary, LeaveApplications
# Register your models here.


admin.site.register(LeaveType)
admin.site.register(LeaveSummary)
admin.site.register(LeaveApplications)
