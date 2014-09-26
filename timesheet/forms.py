from django import forms
from timesheet.models import Project

# Read http://pydanny.com/core-concepts-django-modelforms.html for better
# understanding of Django Forms


class CreateProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = (
            'startDate',
            'endDate',
            'plannedEffort',
            'contingencyEffort',
            'projectManager', )

# This form is used in the initial login screen


class LoginForm(forms.Form):
    userid = forms.CharField(max_length=30)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)
