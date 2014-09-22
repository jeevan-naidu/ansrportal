from django.contrib import admin
from timesheet.models import project, timeSheetEntry, ProjectChangeInfo, ProjectMilestone, ProjectTeamMember

# Register your models here.

class projectAdmin(admin.ModelAdmin):
    list_display = ('name', 'startDate', 'endDate', 'plannedEffort', 'projectManager')
    search_fields = ('name', 'projectManager')

class timeSheetEntryAdmin(admin.ModelAdmin):
    list_display = ('project')
    search_fields = ('project')

class projectChangeInfoAdmin(admin.ModelAdmin):
    list_display = ('firstName', 'emailAddress', 'ResidentialAddress', 'mobileNumber')
    search_fields = ('firstName', 'mobileNumber')

class projectMileStoneAdmin(admin.ModelAdmin):
    list_display = ('docName', 'specialization', 'experience')
    search_fields = ('specialization','docName')

class projectTeamMemberAdmin(admin.ModelAdmin):
    list_display = ('firstName', 'emailAddress', 'ResidentialAddress', 'mobileNumber')
    search_fields = ('firstName', 'mobileNumber')

admin.site.register(project)
admin.site.register(timeSheetEntry)
admin.site.register(ProjectChangeInfo)
admin.site.register(ProjectMilestone)
admin.site.register(ProjectTeamMember)
