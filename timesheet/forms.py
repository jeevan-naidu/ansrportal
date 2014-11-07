from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from timesheet.models import Project, ProjectTeamMember, \
    ProjectMilestone, TimeSheetEntry, Chapter
from bootstrap3_datetime.widgets import DateTimePicker
from smart_selects.form_fields import ChainedModelChoiceField

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
        self.fields['activity_monday'].widget.attrs['class'] = "form-control \
        days input-field"
        self.fields['activity_tuesday'].widget.attrs['class'] = "form-control \
        days input-field"
        self.fields['activity_wednesday'].widget.attrs['class'] = "form-control \
        days input-field"
        self.fields['activity_thursday'].widget.attrs['class'] = "form-control \
        days input-field"
        self.fields['activity_friday'].widget.attrs['class'] = "form-control \
        days input-field"
        self.fields['activity_saturday'].widget.attrs['class'] = "form-control \
        days input-field"
        self.fields['activity_total'].widget.attrs['class'] = "form-control \
        total input-field"
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
def TimesheetFormset(currentUser):
    class TimeSheetEntryForm(forms.Form):
        project = forms.ModelChoiceField(
            queryset=None,
            label="Project Name",
            required=True
        )
        chapter = ChainedModelChoiceField(
            'timesheet',
            'Chapter',
            chain_field='project',
            model_field='project',
            show_all=False,
            auto_choose=True
        )
        task = forms.ChoiceField(choices=TASK, label='Task')
        monday = forms.CharField(label="Mon")
        mondayQ = forms.IntegerField(label="Hours")
        mondayH = forms.IntegerField(label="Questions")
        tuesday = forms.CharField(label="Tue",)
        tuesdayQ = forms.IntegerField(label="Hours")
        tuesdayH = forms.IntegerField(label="Questions")
        wednesday = forms.CharField(label="Wed")
        wednesdayQ = forms.IntegerField(label="Hours")
        wedbesdayH = forms.IntegerField(label="Questions")
        thursday = forms.CharField(label="Thu")
        thursdayQ = forms.IntegerField(label="Hours")
        thursdayH = forms.IntegerField(label="Questions")
        friday = forms.CharField(label="Fri")
        fridayQ = forms.IntegerField(label="Hours")
        fridayH = forms.IntegerField(label="Questions")
        saturday = forms.CharField(label="Sat")
        saturdayQ = forms.IntegerField(label="Hours")
        saturdayH = forms.IntegerField(label="Questions")
        total = forms.CharField(label="Total", required=False)
        totalQ = forms.IntegerField(label="Hours")
        totalH = forms.IntegerField(label="Questions")
        feedback = forms.CharField(
            max_length="50", label="Feedback", required=False
        )

        def __init__(self, *args, **kwargs):
            super(TimeSheetEntryForm, self).__init__(*args, **kwargs)
            self.fields['project'].queryset = Project.objects.filter(
                id__in=ProjectTeamMember.objects.filter(
                    member=currentUser.id
                ).values('project_id')
            )
            self.fields['project'].widget.attrs['class'] = "form-control"
            self.fields['chapter'].widget.attrs['class'] = "form-control"
            self.fields['task'].widget.attrs['class'] = "form-control"
            self.fields['monday'].widget.attrs['value'] = 0
            self.fields['tuesday'].widget.attrs['value'] = 0
            self.fields['wednesday'].widget.attrs['value'] = 0
            self.fields['thursday'].widget.attrs['value'] = 0
            self.fields['friday'].widget.attrs['value'] = 0
            self.fields['saturday'].widget.attrs['value'] = 0
            self.fields['monday'].widget.attrs['class'] = "form-control \
            days input-field"
            self.fields['tuesday'].widget.attrs['class'] = "form-control \
            days input-field"
            self.fields['wednesday'].widget.attrs['class'] = "form-control \
            days input-field"
            self.fields['thursday'].widget.attrs['class'] = "form-control \
            days input-field"
            self.fields['friday'].widget.attrs['class'] = "form-control \
            days input-field"
            self.fields['saturday'].widget.attrs['class'] = "form-control \
            days input-field"
            self.fields['total'].widget.attrs['class'] = "form-control \
            total input-field"
            self.fields['total'].widget.attrs['value'] = "0"
            self.fields['feedback'].widget.attrs['class'] = "form-control"
            self.fields['feedback'].widget.attrs['readonly'] = True
            self.fields['total'].widget.attrs['readonly'] = True
    return TimeSheetEntryForm


# Form Class to create project
class ProjectBasicInfoForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = (
            'bu',
            'name',
            'startDate',
            'endDate',
            'chapters',
            'plannedEffort',
            'contingencyEffort',
            'totalValue'
        )
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
            'deliverables',
            'amount'
        )
        widgets = {
            'milestoneDate': DateTimePicker(options=dateTimeOption),
            'project': forms.HiddenInput(), }


# Form Class to create front-End Login
class LoginForm(forms.Form):
    userid = forms.CharField(max_length=30)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)
