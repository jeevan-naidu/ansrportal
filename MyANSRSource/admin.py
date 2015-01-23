from django.contrib import admin
from MyANSRSource.models import Project, TimeSheetEntry, \
    ProjectMilestone, ProjectTeamMember, Book, Chapter, \
    ProjectChangeInfo, projectType


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 2
    exclude = []


# Admin Models for ansr
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    # which fields should appear on the filter column
    list_filter = ['name', 'author']
    # Search capabilitiy
    search_fields = ['name', 'author']
    # Which of the fields can be edited in list mode
    # list_editable = ['']
    # Ordering of the books
    ordering = ['-updatedOn']
    # Inline forms
    inlines = [ChapterInline, ]


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'startDate', 'endDate',
                    'plannedEffort', 'contingencyEffort', 'projectManager')
    search_fields = ('name', 'projectManager', 'startDate', 'endDate')
    filter_fields = ('startDate', 'endDate')


class projectTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'description',)


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
    list_display = ('milestoneDate', 'description')


class ProjectTeamMemberAdmin(admin.ModelAdmin):
    list_display = ('member', 'role',
                    'startDate', 'plannedEffort')

admin.site.register(Project, ProjectAdmin)
admin.site.register(TimeSheetEntry, TimeSheetEntryAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(projectType, projectTypeAdmin)
#admin.site.register(ProjectChangeInfo, ProjectChangeInfoAdmin)
admin.site.register(ProjectMilestone, ProjectMileStoneAdmin)
admin.site.register(ProjectTeamMember, ProjectTeamMemberAdmin)
