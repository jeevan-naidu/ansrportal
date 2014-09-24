from django.contrib import admin
from timesheet.models import project, timeSheetEntry, ProjectChangeInfo, \
    ProjectMilestone, ProjectTeamMember

# Admin Models for ansr


class projectAdmin(admin.ModelAdmin):
    list_display = ('name', 'startDate', 'endDate',
                    'plannedEffort', 'projectManager')
    search_fields = ('name', 'projectManager')


class timeSheetEntryAdmin(admin.ModelAdmin):
    list_display = ['project']
    # search_fields = ('project')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['managerFeedback']
        return self.readonly_fields


class projectChangeInfoAdmin(admin.ModelAdmin):
    list_display = ('firstName', 'emailAddress',
                    'ResidentialAddress', 'mobileNumber')
    search_fields = ('firstName', 'mobileNumber')


class projectMileStoneAdmin(admin.ModelAdmin):
    list_display = ('docName', 'specialization', 'experience')
    search_fields = ('specialization', 'docName')


class projectTeamMemberAdmin(admin.ModelAdmin):
    list_display = ('firstName', 'emailAddress',
                    'ResidentialAddress', 'mobileNumber')
    search_fields = ('firstName', 'mobileNumber')

admin.site.register(project, projectAdmin)
admin.site.register(timeSheetEntry, timeSheetEntryAdmin)
admin.site.register(ProjectChangeInfo)
admin.site.register(ProjectMilestone)
admin.site.register(ProjectTeamMember)
