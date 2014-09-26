from django.contrib import admin
from timesheet.models import Project, TimeSheetEntry, ProjectChangeInfo, \
    ProjectMilestone, ProjectTeamMember

# Admin Models for ansr


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'startDate', 'endDate',
                    'plannedEffort', 'projectManager')
    search_fields = ('name', 'projectManager')


class TimeSheetEntryAdmin(admin.ModelAdmin):
    list_display = ['project']
    # search_fields = ('project')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['managerFeedback']
        return self.readonly_fields


class ProjectChangeInfoAdmin(admin.ModelAdmin):
    list_display = ('firstName', 'emailAddress',
                    'ResidentialAddress', 'mobileNumber')
    search_fields = ('firstName', 'mobileNumber')


class ProjectMileStoneAdmin(admin.ModelAdmin):
    list_display = ('docName', 'specialization', 'experience')
    search_fields = ('specialization', 'docName')


class ProjectTeamMemberAdmin(admin.ModelAdmin):
    list_display = ('firstName', 'emailAddress',
                    'ResidentialAddress', 'mobileNumber')
    search_fields = ('firstName', 'mobileNumber')

admin.site.register(Project, ProjectAdmin)
admin.site.register(TimeSheetEntry, TimeSheetEntryAdmin)
#admin.site.register(ProjectChangeInfo, ProjectChangeInfoAdmin)
#admin.site.register(ProjectMilestone, ProjectMileStoneAdmin)
#admin.site.register(ProjectTeamMember, ProjectTeamMemberAdmin)
