from django import forms
from timesheet.models import Project, ProjectTeamMember, ProjectMilestone
from django.forms.extras.widgets import SelectDateWidget


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
            'startDate': SelectDateWidget(),
            'endDate': SelectDateWidget(),
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
            'project': forms.HiddenInput(), }


# Form Class to create milestones for project
class ProjectMilestoneForm(forms.ModelForm):

    class Meta:
        model = ProjectMilestone
        fields = (
            'milestoneDate',
            'deliverables', )
        widgets = {
            'project': forms.HiddenInput(), }


# Form Class to create front-End Login
class LoginForm(forms.Form):
    userid = forms.CharField(max_length=30)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)
