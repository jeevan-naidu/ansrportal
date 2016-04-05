from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.contrib.auth.models import User
from Grievances.models import Grievances, Grievances_catagory,  STATUS_CHOICES_CLOSED
import autocomplete_light
autocomplete_light.autodiscover()

dateTimeOption = {"format": "DD/MM/YYYY", "pickTime": False}
STATUS_CHOICES_EMPTY = (('', '---------'),) + STATUS_CHOICES_CLOSED


class FilterGrievanceForm(autocomplete_light.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True),
                                  widget=autocomplete_light.ChoiceWidget('UserAutocompleteUser'))

    user.widget.attrs = {'class': 'form-control filter_class', 'placeholder': 'Enter Employee Name'}

    catagory = forms.ModelChoiceField(queryset=Grievances_catagory.objects.filter(active=True), empty_label="---------")

    catagory.widget.attrs = {'class': 'form-control filter_class'}

    grievance_status = forms.ChoiceField(choices=STATUS_CHOICES_EMPTY)

    grievance_status.widget.attrs = {'class': 'form-control filter_class'}

    created_date = forms.DateField(
        label="From",
        widget=DateTimePicker(options=dateTimeOption),
    )
    created_date.widget.attrs = {'class': 'form-control filter_class'}

    closure_date = forms.DateField(
        label="To",
        widget=DateTimePicker(options=dateTimeOption),
    )
    closure_date.widget.attrs = {'class': 'form-control filter_class'}

    class Meta:
        model = Grievances
        fields = ['catagory', 'grievance_status', 'created_date', 'closure_date']
        fields = (
            'user',
        )

