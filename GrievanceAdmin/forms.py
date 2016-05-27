from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.contrib.auth.models import User
from Grievances.models import Grievances, Grievances_category,  STATUS_CHOICES_CLOSED
import autocomplete_light
autocomplete_light.autodiscover()

dateTimeOption = {"format": "DD/MM/YYYY", "pickTime": False}
STATUS_CHOICES_EMPTY = (('', '---------'),) + STATUS_CHOICES_CLOSED


class FilterGrievanceForm(autocomplete_light.ModelForm):

    grievance_id = forms.ModelChoiceField(queryset=Grievances.objects.all(),
                                          widget=autocomplete_light.ChoiceWidget('GrievancesAutocompleteGrievanceAdmin'))

    grievance_id.widget.attrs = {'class': 'form-control filter_class', 'placeholder': 'Enter Grievance Id'}

    user = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True),
                                  widget=autocomplete_light.ChoiceWidget('UserAutocompleteUser'))

    user.widget.attrs = {'class': 'form-control filter_class', 'placeholder': 'Enter Employee Name'}

    category = forms.ModelChoiceField(queryset=Grievances_category.objects.filter(active=True), empty_label="---------")

    category.widget.attrs = {'class': 'form-control filter_class'}

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
        fields = ['category', 'grievance_status', 'created_date', 'closure_date']
        fields = (
            'user', 'grievance_id',
        )

