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
