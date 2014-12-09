from django.contrib import admin
from MyANSRSource.models import Project, TimeSheetEntry, \
    ProjectMilestone, ProjectTeamMember, Book, Chapter


# Admin Models for ansr
class BookAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ChapterAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'startDate', 'endDate',
                    'plannedEffort', 'contingencyEffort', 'projectManager')
    search_fields = ('name', 'projectManager', 'startDate', 'endDate')
    filter_fields = ('startDate', 'endDate')


class TimeSheetEntryAdmin(admin.ModelAdmin):
    list_display = ['project']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['managerFeedback']
        return self.readonly_fields


class ProjectChangeInfoAdmin(admin.ModelAdmin):
    list_display = ('firstName', 'emailAddress',
                    'ResidentialAddress', 'mobileNumber')
    search_fields = ('firstName', 'mobileNumber')


class ProjectMileStoneAdmin(admin.ModelAdmin):
    list_display = ('milestoneDate', 'deliverables', 'description')


class ProjectTeamMemberAdmin(admin.ModelAdmin):
    list_display = ('member', 'role',
                    'startDate', 'plannedEffort')

admin.site.register(Project, ProjectAdmin)
admin.site.register(TimeSheetEntry, TimeSheetEntryAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Chapter, ChapterAdmin)
# admin.site.register(ProjectChangeInfo, ProjectChangeInfoAdmin)
admin.site.register(ProjectMilestone, ProjectMileStoneAdmin)
admin.site.register(ProjectTeamMember, ProjectTeamMemberAdmin)
