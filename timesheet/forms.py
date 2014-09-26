from django import forms
from timesheet.models import project


class createProjectForm(forms.ModelForm):
    name = forms.CharField(max_length=256)

    class Meta:
        model = project
