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

