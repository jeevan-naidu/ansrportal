from django import forms
from timesheet.models import Project, ProjectTeamMember, ProjectMilestone
# from widgets import DateWidget
from datetimewidget.widgets import DateWidget
from widgets import BootstrapUneditableInput


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


class snapshotForm(forms.Form):
    name = forms.CharField(
        label="Project Name",
        widget=forms.TextInput(
            attrs={'readonly': 'True'}
        )
    )
    projectStartDate = forms.CharField(
        label="Project Start date",
        widget=forms.TextInput(
            attrs={'readonly': 'True'}
        )
    )
    projectEndDate = forms.CharField(
        label="Project End date",
        widget=forms.TextInput(
            attrs={'readonly': 'True'}
        )
    )
    plannedEffort = forms.CharField(
        label="Project Planned Effort",
        widget=BootstrapUneditableInput()
    )
    contingencyEffort = forms.CharField(
        label="Project Contigency Effort",
        widget=BootstrapUneditableInput()
    )
    member = forms.CharField(
        label="Project Member",
        widget=BootstrapUneditableInput()
    )
    role = forms.CharField(
        label="Member Role",
        widget=BootstrapUneditableInput()
    )
    plannedEffort = forms.CharField(
        label="Member Effort",
        widget=BootstrapUneditableInput()
    )
    memberStartDate = forms.CharField(
        label="Member Start Date",
        widget=BootstrapUneditableInput()
    )
    milestoneDate = forms.CharField(
        label="Milestone Date",
        widget=BootstrapUneditableInput()
    )
    description = forms.CharField(
        label="Description",
        widget=BootstrapUneditableInput()
    )
    deliverables = forms.CharField(
        label="Deliverables",
        widget=BootstrapUneditableInput()
    )


# Form Class to create front-End Login
class LoginForm(forms.Form):
    userid = forms.CharField(max_length=30)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)
