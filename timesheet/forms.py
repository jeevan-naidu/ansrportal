from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from timesheet.models import Project, ProjectTeamMember, \
    ProjectMilestone, TimeSheetEntry, Chapter
from bootstrap3_datetime.widgets import DateTimePicker
from smart_selects.db_fields import ChainedForeignKey

dateTimeOption = {"format": "YYYY-MM-DD", "pickTime": False}

TASK = (
    ('D', 'Develop'),
    ('R', 'Review'),
    ('C', 'Copy Edit'),
    ('Q', 'QA'),
    ('I', 'Idle'),
)

NONBILLABLE = (
    ('S', 'Self Development'),
    ('R', 'Leave'),
    ('C', 'Training'),
    ('Q', 'Others'),
)

class ActivityForm(forms.Form):
    activity = forms.ChoiceField(choices=NONBILLABLE, label="Activity")
    activity_monday = forms.IntegerField(
        label="Mon",
        min_value=0,
        max_value=24
    )
    activity_tuesday = forms.IntegerField(
        label="Tue",
        min_value=0,
        max_value=24
    )
    activity_wednesday = forms.IntegerField(
        label="Wed",
        min_value=0,
        max_value=24
    )
    activity_thursday = forms.IntegerField(
        label="Thu",
        min_value=0,
        max_value=24
    )
    activity_friday = forms.IntegerField(
        label="Fri",
        min_value=0,
        max_value=24
    )
    activity_saturday = forms.IntegerField(
        label="Sat",
        min_value=0,
        max_value=24
    )
    activity_total = forms.IntegerField(
        label="Total",
        min_value=0,
        max_value=144,
        required=False
    )
    activity_feedback = forms.CharField(
        max_length="50", label="Feedback", required=False
    )

    def __init__(self, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)
        self.fields['activity_feedback'].widget.attrs['readonly'] = True
        self.fields['activity_total'].widget.attrs['readonly'] = True
        self.fields['activity'].widget.attrs['class'] = "form-control"
        self.fields['activity_monday'].widget.attrs['class'] = "form-control days input-field"
        self.fields['activity_tuesday'].widget.attrs['class'] = "form-control days input-field"
        self.fields['activity_wednesday'].widget.attrs['class'] = "form-control days input-field"
        self.fields['activity_thursday'].widget.attrs['class'] = "form-control days input-field"
        self.fields['activity_friday'].widget.attrs['class'] = "form-control days input-field"
        self.fields['activity_saturday'].widget.attrs['class'] = "form-control days input-field"
        self.fields['activity_total'].widget.attrs['class'] = "form-control total input-field"
        self.fields['activity_feedback'].widget.attrs['class'] = "form-control"
        self.fields['activity_monday'].widget.attrs['value'] = 0
        self.fields['activity_tuesday'].widget.attrs['value'] = 0
        self.fields['activity_wednesday'].widget.attrs['value'] = 0
        self.fields['activity_thursday'].widget.attrs['value'] = 0
        self.fields['activity_friday'].widget.attrs['value'] = 0
        self.fields['activity_saturday'].widget.attrs['value'] = 0
        self.fields['activity_total'].widget.attrs['value'] = 0


class ChapterForm(forms.ModelForm):

    class Meta:
        model = Chapter
        fields = ('name',)


# Form class to maintain timesheet records
class TimeSheetEntryForm(forms.Form):
    myProjects = Project.objects.all()
    myChapters = Chapter.objects.all()
    project = forms.ModelChoiceField(
        queryset=myProjects,
        label="Project Name"
    )
    chapter = forms.ModelChoiceField(
        queryset=myChapters,
        label="Chapter"
    )
    task = forms.ChoiceField(choices=TASK, label='Task' )
    monday = forms.IntegerField(
        label="Mon",
        min_value=0,
        max_value=24
    )
    tuesday = forms.IntegerField(
        label="Tue",
        min_value=0,
        max_value=24
    )
    wednesday = forms.IntegerField(
        label="Wed",
        min_value=0,
        max_value=24
    )
    thursday = forms.IntegerField(
        label="Thu",
        min_value=0,
        max_value=24
    )
    friday = forms.IntegerField(
        label="Fri",
        min_value=0,
        max_value=24
    )
    saturday = forms.IntegerField(
        label="Sat",
        min_value=0,
        max_value=24
    )
    total = forms.IntegerField(
        label="Total",
        min_value=0,
        max_value=144,
        required=False
    )
    feedback = forms.CharField(
        max_length="50", label="Feedback", required=False
    )

    def __init__(self, *args, **kwargs):
        super(TimeSheetEntryForm, self).__init__(*args, **kwargs)
        self.fields['project'].widget.attrs['class'] = "form-control"
        self.fields['chapter'].widget.attrs['class'] = "form-control"
        self.fields['task'].widget.attrs['class'] = "form-control"
        self.fields['monday'].widget.attrs['value'] = 0
        self.fields['tuesday'].widget.attrs['value'] = 0
        self.fields['wednesday'].widget.attrs['value'] = 0
        self.fields['thursday'].widget.attrs['value'] = 0
        self.fields['friday'].widget.attrs['value'] = 0
        self.fields['saturday'].widget.attrs['value'] = 0
        self.fields['monday'].widget.attrs['class'] = "form-control days input-field"
        self.fields['tuesday'].widget.attrs['class'] = "form-control days input-field"
        self.fields['wednesday'].widget.attrs['class'] = "form-control days input-field"
        self.fields['thursday'].widget.attrs['class'] = "form-control days input-field"
        self.fields['friday'].widget.attrs['class'] = "form-control days input-field"
        self.fields['saturday'].widget.attrs['class'] = "form-control days input-field"
        self.fields['total'].widget.attrs['class'] = "form-control total input-field"
        self.fields['total'].widget.attrs['value'] = "0"
        self.fields['feedback'].widget.attrs['class'] = "form-control"
        self.fields['feedback'].widget.attrs['readonly'] = True
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
