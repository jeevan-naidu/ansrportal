from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from timesheet.models import Project, ProjectTeamMember, \
    ProjectMilestone, TimeSheetEntry, Chapter
from bootstrap3_datetime.widgets import DateTimePicker

dateTimeOption = {"format": "YYYY-MM-DD", "pickTime": False}


class ActivityForm(forms.ModelForm):

    class Meta:
        model = TimeSheetEntry
        fields = (
            'activity',
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'total',
            'managerFeedback'
        )

    def __init__(self, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)
        self.fields['monday'].widget.attrs['id'] = 'id_activityMonday'
        self.fields['tuesday'].widget.attrs['id'] = 'id_activityTuesday'
        self.fields['wednesday'].widget.attrs['id'] = 'id_activityWednesday'
        self.fields['thursday'].widget.attrs['id'] = 'id_activityThursday'
        self.fields['friday'].widget.attrs['id'] = 'id_activityFriday'
        self.fields['saturday'].widget.attrs['id'] = 'id_activitySaturday'
        self.fields['total'].widget.attrs['id'] = 'id_activityTotal'
        self.fields['managerFeedback'].widget.attrs['readonly'] = True
        self.fields['total'].widget.attrs['readonly'] = True


class ChapterForm(forms.ModelForm):

    class Meta:
        model = Chapter
        fields = ('name',)


# Form class to maintain timesheet records
class TimeSheetEntryForm(forms.ModelForm):

    class Meta:
        model = TimeSheetEntry
        fields = (
            'project',
            'chapter',
            'task',
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'total',
            'managerFeedback'
        )

    def __init__(self, *args, **kwargs):
        super(TimeSheetEntryForm, self).__init__(*args, **kwargs)
        self.fields['project'].widget.attrs['class'] = "form-control"
        self.fields['chapter'].widget.attrs['class'] = "form-control"
        self.fields['task'].widget.attrs['class'] = "form-control"
        self.fields['monday'].widget.attrs['class'] = "form-control"
        self.fields['tuesday'].widget.attrs['class'] = "form-control"
        self.fields['wednesday'].widget.attrs['class'] = "form-control"
        self.fields['thursday'].widget.attrs['class'] = "form-control"
        self.fields['friday'].widget.attrs['class'] = "form-control"
        self.fields['saturday'].widget.attrs['class'] = "form-control"
        self.fields['total'].widget.attrs['class'] = "form-control"
        self.fields['managerFeedback'].widget.attrs['class'] = "form-control"
        self.fields['managerFeedback'].widget.attrs['readonly'] = True
        self.fields['total'].widget.attrs['readonly'] = True


# Form Class to create project
class ProjectBasicInfoForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = (
            'name',
            'startDate',
            'endDate',
            'plannedEffort',
            'contingencyEffort', )
        widgets = {
            'startDate': DateTimePicker(options=dateTimeOption),
            'endDate': DateTimePicker(options=dateTimeOption),
            'projectManager': forms.HiddenInput(), }


# Form Class to create team for project
class ProjectTeamForm(forms.ModelForm):

    class Meta:
        model = ProjectTeamMember
        fields = (
            'member',
            'role',
            'plannedEffort',
            'startDate', )
        widgets = {
            'startDate': DateTimePicker(options=dateTimeOption),
            'project': forms.HiddenInput(), }

    def __init__(self, *args, **kwargs):
        super(ProjectTeamForm, self).__init__(*args, **kwargs)
        self.fields['member'].queryset = User.objects.exclude(
            Q(groups__name='project manager') |
            Q(is_superuser=True)
        )


# Form Class to create milestones for project
class ProjectMilestoneForm(forms.ModelForm):

    class Meta:
        model = ProjectMilestone
        fields = (
            'milestoneDate',
            'description',
            'deliverables', )
        widgets = {
            'milestoneDate': DateTimePicker(options=dateTimeOption),
            'project': forms.HiddenInput(), }


# Form Class to create front-End Login
class LoginForm(forms.Form):
    userid = forms.CharField(max_length=30)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)
