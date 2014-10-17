from django import forms
from timesheet.models import Project, ProjectTeamMember, ProjectMilestone
# from widgets import DateWidget
from datetimewidget.widgets import DateWidget


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
            'startDate': DateWidget(bootstrap_version=3),
            'endDate': DateWidget(bootstrap_version=3),
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
            'startDate': DateWidget(bootstrap_version=3),
            'project': forms.HiddenInput(), }


# Form Class to create milestones for project
class ProjectMilestoneForm(forms.ModelForm):

    class Meta:
        model = ProjectMilestone
        fields = (
            'milestoneDate',
            'description',
            'deliverables', )
        widgets = {
            'milestoneDate': DateWidget(bootstrap_version=3),
            'project': forms.HiddenInput(), }


# Form Class to create front-End Login
class LoginForm(forms.Form):
    userid = forms.CharField(max_length=30)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)
