from django import forms
from MyANSRSource.models import Project
import autocomplete_light
from bootstrap3_datetime.widgets import DateTimePicker

autocomplete_light.autodiscover()

dateTimeOption = {"format": "MM/DD/YYYY", "pickTime": False}
MILESTONE_CHOICES = (('any', 'Any'), ('financial', 'Financial'), ('non_financial', 'Non-Financial'))
MILESTONE_STATUS_CHOICES = (('any', 'Any'), ('completed', 'Completed'), ('not_completed', 'Not Completed'))


class MilestoneReportsForm(forms.Form):
    project = forms.ModelChoiceField(help_text="Leave blank for all", queryset=Project.objects.all(),
                                     widget=autocomplete_light.ChoiceWidget('ProjectAutocompleteProjects'),
                                     required=False)

    project.widget.attrs = {'class': 'form-control', 'placeholder': 'Enter Project Id/Name'}

    from_date = forms.DateField(label="From", widget=DateTimePicker(options=dateTimeOption),
    )
    from_date.widget.attrs = {'class': 'form-control filter_class', 'required': 'true'}

    to_date = forms.DateField(label="To", widget=DateTimePicker(options=dateTimeOption),
    )
    to_date.widget.attrs = {'class': 'form-control filter_class', 'required': 'true'}

    milestone_type = forms.ChoiceField(choices=MILESTONE_CHOICES)
    milestone_type.widget.attrs = {'class': 'form-control'}

    milestone_status = forms.ChoiceField(choices=MILESTONE_STATUS_CHOICES)
    milestone_status.widget.attrs = {'class': 'form-control'}

    def clean(self):
        # cleaned_data = super(MilestoneReportsForm, self).clean()
        from_date = self.cleaned_data.get('from_date')
        to_date = self.cleaned_data.get('to_date')
        if from_date > to_date:
            self.add_error('from_date', "From date should be less than to date")
