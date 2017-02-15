from django import forms
from django.contrib import admin
from django.contrib import messages

from MyANSRSource.models import Project, ProjectManager, \
    ProjectMilestone, Book, Chapter, \
    projectType, Task, Activity, Report,\
    TimeSheetEntry, Milestone, MilestoneType


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
    search_fields = ['name', 'edition', 'author', 'isbn', 'active']
    fields = ('name', 'edition', 'author', 'isbn', 'active')
    # Which of the fields can be edited in list mode
    # list_editable = ['']
    # Ordering of the books
    ordering = ['-updatedOn']
    # Inline forms
    inlines = [ChapterInline, ]

    def save_model(self, request, obj, form, change):
        isbn = str(getattr(obj, 'isbn'))
        try:
            if len(isbn)<14:
                for digit in isbn:
                    int(digit)
                obj.save()
            else:
                messages.error(request, "Digit need to be less than 13 digit")
                messages.success(request,"")


        except ValueError:
            messages.error(request, "Please enter only digits")
            messages.success(request,"")

class ProjectMilestoneInline(admin.TabularInline):
    model = ProjectMilestone
    extra = 0


class ProjectManagerM2MInline(admin.TabularInline):
    model = ProjectManager
    extra = 1


class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'projectId',
        'name',
        'startDate',
        'endDate',
        'plannedEffort',
        'contingencyEffort',
        'totalValue',
        'PracticeName',
        'SubPractice',
        'projectFinType',
        'PracticeHead',
        'deliveryManager')
    fieldsets = [
        ('Basic Information', {
            'fields': [
                'bu', 'projectType', 'customer', 'customerContact', 'projectId', 'name', ], },), ('Status', {
            'fields': [
                'currentProject', 'signed', 'internal', 'po', 'salesForceNumber', 'closed', ], }, ), ('Time and Money', {
            'fields': [
                'startDate', 'endDate', 'plannedEffort', 'contingencyEffort', 'totalValue', ], }, ), ]
    inlines = (ProjectManagerM2MInline, ProjectMilestoneInline, )

    def get_queryset(self, request):
        qs = super(ProjectAdmin, self).get_queryset(request)
        # or request.user.has_perm('MyANSRSource.view_all_projects'):
        if request.user.is_superuser:
            return qs.filter()
        else:
            return qs.filter(closed=False, projectManager=request.user)
    search_fields = (
        'projectId',
        'name',
        'customer__name',
        'projectManager__username',)

    list_filter = ('bu__name', 'startDate', 'endDate', 'book')
    ordering = ['-updatedOn']

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
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


class projectTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'description',)
    def get_queryset(self, request):
        qs = super(projectTypeAdmin, self).get_queryset(request)
        return qs.filter(active=True)


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
    list_display = ('projectType', 'name', 'taskType', 'norm')
    filter_fields = ('projectType',)
    ordering = ['projectType', 'name', ]
    search_fields = ['name', ]
    def get_queryset(self, request):
        qs = super(TaskAdmin, self).get_queryset(request)
        return qs.filter(active=True)


class ProjectTeamMemberAdmin(admin.ModelAdmin):
    list_display = ('member', 'role',
                    'startDate', 'plannedEffort')


def update_timesheet(modeladmin, request, queryset):
    queryset.update(approved=0, hold=0)
update_timesheet.short_description = "Cancel Approved Timesheet"


class TimeSheetEntryAdmin(admin.ModelAdmin):
    list_display = ('teamMember', 'wkstart', 'wkend')
    filter_fields = ('wkstart', 'wkend')
    ordering = ['wkstart', 'wkend']
    search_fields = ['teamMember__first_name', 'teamMember__last_name', 'teamMember__username']
    actions = [update_timesheet]

    def get_queryset(self, request):
        qs = super(TimeSheetEntryAdmin, self).get_queryset(request).distinct()
        qs = qs.filter(approved=1, hold=1)
        return qs


class MilestoneTypeAdmin(admin.ModelAdmin):
    list_display = ('milestone_type', 'is_financial')


class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'milestone_type', 'is_final_milestone', 'check_schedule_deviation')


admin.site.register(Project, ProjectAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(projectType, projectTypeAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TimeSheetEntry, TimeSheetEntryAdmin)
admin.site.register(MilestoneType, MilestoneTypeAdmin)
admin.site.register(Milestone, MilestoneAdmin)

