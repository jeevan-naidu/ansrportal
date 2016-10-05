from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.contrib.auth.models import User
from Grievances.models import Grievances, Grievances_category,  STATUS_CHOICES_CLOSED
from dal import autocomplete

dateTimeOption = {"format": "DD/MM/YYYY", "pickTime": False}
STATUS_CHOICES_EMPTY = (('', '---------'),) + STATUS_CHOICES_CLOSED


class FilterGrievanceForm(forms.ModelForm):

    grievance_id = forms.ModelChoiceField(
        queryset=Grievances.objects.all(),
        # label="Book/Title",
        widget=autocomplete.ModelSelect2(url='AutocompleteGrievanceAdmin', attrs={
            # Set some placeholder
            'data-placeholder': 'Enter Grievance Id ...',
            #'class': 'form-control filter_class'
            # Only trigger autocompletion after 3 characters have been typed
            # 'data-minimum-input-length': 3,
        }, ),
        required=False, )

    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        # label="Book/Title",
        widget=autocomplete.ModelSelect2(url='AutocompleteUser', attrs={
            # Set some placeholder
            'data-placeholder': 'Enter Employee Name ...',
            'class': 'form-control filter_class'
            # Only trigger autocompletion after 3 characters have been typed
            # 'data-minimum-input-length': 3,
        }, ),
        required=False, )

    category = forms.ModelChoiceField(queryset=Grievances_category.objects.filter(active=True))

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
        # fields = (
        #     'user', 'grievance_id',
        # )

