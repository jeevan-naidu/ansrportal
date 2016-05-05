from django import forms
from MyANSRSource.models import Project
import autocomplete_light
from bootstrap3_datetime.widgets import DateTimePicker
autocomplete_light.autodiscover()

dateTimeOption = {"format": "DD/MM/YYYY", "pickTime": False}
MILESTONE_CHOICES= (('financial', 'Financial'), ('non_financial','Non-Financial'))
MILESTONE_STATUS_CHOICES= (('completed', 'Completed'), ('not_completed','Not Completed'))

class MilestoneReportsForm(forms.Form):
    
    project = forms.ModelChoiceField(queryset=Project.objects.all(),
                                          widget=autocomplete_light.ChoiceWidget('ProjectAutocompleteProjects'))
    
    project.widget.attrs = {'class': 'form-control', 'placeholder': 'Enter Project Id/Name'}
    
    from_date = forms.DateField(
        label="From",
        widget=DateTimePicker(options=dateTimeOption),
    )
    from_date.widget.attrs = {'class': 'form-control filter_class'}
    
    to_date = forms.DateField(
        label="To",
        widget=DateTimePicker(options=dateTimeOption),
    )
    to_date.widget.attrs = {'class': 'form-control filter_class'}
    
    milestone_type = forms.ChoiceField(choices=MILESTONE_CHOICES)
    milestone_type.widget.attrs = {'class': 'form-control'}
    
    milestone_status = forms.ChoiceField(choices=MILESTONE_STATUS_CHOICES)
    milestone_status.widget.attrs = {'class': 'form-control'}
    
    #project = forms.ModelChoiceField(
    #    queryset=None,
    #    label="Project",
    #    required=True,
    #)
    #
    #def __init__(self, *args, **kwargs):
    #    super(MilestoneReportsForm, self).__init__(*args, **kwargs)
    #    self.fields['project'].queryset = Project.objects.all()
    #    self.fields['project'].widget = autocomplete_light.ChoiceWidget('ProjectAutocompleteProjects')
    #    self.fields['project'].widget.attrs['class'] = "form-control"
    #    self.fields['project'].widget.attrs['placeholder'] = 'Enter a Project Name /Project Id'

 