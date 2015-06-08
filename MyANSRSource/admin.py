from django import forms
from django.contrib import admin

from MyANSRSource.models import Project, ProjectManager, \
    ProjectMilestone, Book, Chapter, \
    projectType, Task, Activity, Report


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
    form = ChapterInlineFormSet


# Admin Models for ansr
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'edition', 'author', 'isbn')
    # which fields should appear on the filter column
    list_filter = ['name', 'edition', 'author', 'isbn']
    # Search capabilitiy
    search_fields = ['name', 'edition', 'author', 'isbn']
    fields = ('name', 'edition', 'author', 'isbn')
    # Which of the fields can be edited in list mode
    # list_editable = ['']
    # Ordering of the books
    ordering = ['-updatedOn']
    # Inline forms
    inlines = [ChapterInline, ]


class ProjectMilestoneInline(admin.TabularInline):
    model = ProjectMilestone
    extra = 1


class ProjectManagerM2MInline(admin.TabularInline):
    model = ProjectManager
    extra = 1


class ProjectAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super(ProjectAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(closed=False, projectManager=request.user)

    list_display = (
        'name',
        'startDate',
        'endDate',
        'plannedEffort',
        'projectId',
        'totalValue')
    search_fields = (
        'name',
        'customer__name',
        'projectManager__username',)

    filter_fields = ('startDate', 'endDate', )
    inlines = (ProjectManagerM2MInline, ProjectMilestoneInline, )

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return [
                'projectId',
            ]
        else:
            return [
                'internal', 'po', 'currentProject',
                'startDate',
                'endDate',
                'plannedEffort',
                'totalValue',
                'projectId',
                'closed',
                ]

    fieldsets = [
        ('Basic Information',
         {'fields': ['bu', 'projectType', 'customer', 'name', ], },),
        ('Status',
         {'fields': ['currentProject',
                     'signed',
                     'internal',
                     'projectId',
                     'po',
                     'closed',
                     ],
          },
         ),
        ('Time and Money',
         {'fields': ['startDate',
                     'endDate',
                     'plannedEffort',
                     ],
          },
         ),
    ]


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


class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', )


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'projectType', 'taskType', 'norm')
    filter_fields = ('projectType',)


class ProjectTeamMemberAdmin(admin.ModelAdmin):
    list_display = ('member', 'role',
                    'startDate', 'plannedEffort')

admin.site.register(Project, ProjectAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(projectType, projectTypeAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Task, TaskAdmin)
