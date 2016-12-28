from django.shortcuts import render
from django import forms
from django.forms import Textarea
from models import ResignationInfo, EmployeeClearanceInfo
from bootstrap3_datetime.widgets import DateTimePicker
from dal import autocomplete
from django.contrib.auth.models import User


dateTimeOption = {"format": "YYYY-MM-DD", "pickTime": False}


# Create your views here.
ReasonOfLeaving = (('', 'Please Select'), ('i was tired', 'tired'), ('Personal growth', 'PersonalGrowth'), ('simply', 'Confidential'),('other','others'))


class UserExitForm(forms.ModelForm):
    last_date = forms.DateField(label=('Select your Last Date'),
                                widget=DateTimePicker(options=dateTimeOption))
    start_date = forms.DateField(label=('Select your Date on which you put the resignation'),
                                widget=DateTimePicker(options=dateTimeOption))
    reason_dropdown = forms.ChoiceField(choices=ReasonOfLeaving, required=True,
                                        label=('Please select the proper reason of leaving'),)
    comment = forms.CharField(required=False, label=('Write your Concern overhere'), )

    class Meta:
        model = ResignationInfo
        fields = ['last_date', 'reason_dropdown', 'comment']


class ResignationAcceptanceForm(forms.ModelForm):
    manager_accepted = forms.BooleanField()
    manager_feedback = forms.Textarea()
    hr_accepted = forms.BooleanField()
    hr_feedback = forms.Textarea()
    last_date_accepted = forms.DateField(label=('select the last date of employee'), widget=DateTimePicker(options=dateTimeOption))
    exit_applicant = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        widget=autocomplete.ModelSelect2(url='resignee_search', attrs={
            'data-placeholder': 'Type Member Name ...',
        }, ), )

    class Meta:
        model = ResignationInfo
        fields = ['manager_accepted', 'hr_accepted', 'last_date_accepted', ]



class ClearanceForm(forms.ModelForm):
    librarian_accepted = forms.BooleanField()
    librarian_feedback = forms.CharField()
    admin_accepted = forms.BooleanField()
    admin_feedback = forms.CharField()
    it_accepted = forms.BooleanField()
    it_feedback = forms.CharField()
    exit_applicant_list = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        widget=autocomplete.ModelSelect2(url='resignee_filter', attrs={
            'data-placeholder': 'Type Member Name ...',
        }, ), )

    class Meta:
        model = EmployeeClearanceInfo
        fields = ['dept_status', 'dept_feedback', 'dept_due']

