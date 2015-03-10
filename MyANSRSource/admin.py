from django import forms
from django.contrib import admin

from MyANSRSource.models import Project, TimeSheetEntry, \
    ProjectMilestone, ProjectTeamMember, Book, Chapter, \
    ProjectChangeInfo, projectType, Task, Activity


class ChapterInlineFormSet(forms.ModelForm):

    class Meta:
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'style': 'width:1024px',
                    })
        }

# widgets = { 'construct_name': forms.TextInput(attrs={'size': 20})


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 2
    exclude = []
    #formset = ChapterInlineFormSet
    form = ChapterInlineFormSet
    # class Meta:
    #    widgets = { 'name' :  forms.TextInput(attrs = {'style' : 'width : 1024px'}),}
    # fieldsets = (
    #    ('Chapters', {
    #        'classes': ('wide', 'extrapretty',),
    #        'fields': ('name',)
    #        }),
    #    )


# Admin Models for ansr
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'edition', 'author')
    # which fields should appear on the filter column
    list_filter = ['name', 'edition', 'author']
    # Search capabilitiy
    search_fields = ['name', 'edition', 'author']
    fields = ('name', 'edition', 'author')
    # Which of the fields can be edited in list mode
    # list_editable = ['']
    # Ordering of the books
    ordering = ['-updatedOn']
    # Inline forms
    inlines = [ChapterInline, ]


class ProjectMilestoneInline(admin.TabularInline):
    model = ProjectMilestone
    extra = 1


class ProjectAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super(ProjectAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(closed=False, projectManager=request.user)

    list_display = (
        'name',
        'startDate',
        'endDate',
        'plannedEffort',
        'contingencyEffort',
        'projectId',
        'totalValue')
    search_fields = (
        'name',
        'projectManager',
        'startDate',
        'endDate',
        'customer')
    filter_fields = ('startDate', 'endDate', 'projectManager')
    inlines = [ProjectMilestoneInline, ]


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


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', )


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'projectType', 'taskType', )
    filter_fields = ('projectType',)


class ProjectTeamMemberAdmin(admin.ModelAdmin):
    list_display = ('member', 'role',
                    'startDate', 'plannedEffort')

admin.site.register(Project, ProjectAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(projectType, projectTypeAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Task, TaskAdmin)
