from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from timesheet.models import Project, ProjectTeamMember, ProjectMilestone
from widgets import BootstrapUneditableInput
from bootstrap3_datetime.widgets import DateTimePicker

dateTimeOption = {"format": "YYYY-MM-DD", "pickTime": False}


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
