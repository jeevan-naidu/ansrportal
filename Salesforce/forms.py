from django import forms
from models import SalesforceData
from bootstrap3_datetime.widgets import DateTimePicker
dateTimeOption = {"format": "MM/DD/YYYY", "pickTime": False}

class UploadSalesforceDataForm(forms.Form):
    salesforce_data_file = forms.FileField(required=True, help_text="Please use semicolon delimited csv only")
    salesforce_data_file.widget.attrs = {'class': 'filestyle', 'data-buttonBefore': 'true',
                                         'data-iconName': 'glyphicon glyphicon-paperclip'}


class SalesforceDataForm(forms.ModelForm):

    opportunity_number = forms.CharField(max_length=8, widget=forms.TextInput(attrs={'class': 'input-sm form-control width-40',
                                                                              'required': 'True',
                                                                              'data-error': 'Enter the SFID number'}))
    opportunity_name = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'input-sm form-control width-40', 'required': 'True'}))
    value = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'input-sm form-control width-40', 'required': 'True'}))
    estimate_start_date = forms.DateField(label=('Estimated Start Date'),
                                widget=DateTimePicker(options=dateTimeOption, attrs = {'class': 'form-control input-sm', 'required':''}))
    estimate_end_date = forms.DateField(label=('Estimated End Date'),
                                widget=DateTimePicker(options=dateTimeOption, attrs = {'class': 'form-control input-sm', 'required':''}))
    planned_start_date = forms.DateField(label=('Planned Start Date'),
                                 widget=DateTimePicker(options=dateTimeOption,
                                                       attrs={'class': 'form-control input-sm', 'required': ''}))
    planned_end_date = forms.DateField(label=('Planned End Date'),
                               widget=DateTimePicker(options=dateTimeOption,
                                                     attrs={'class': 'form-control input-sm', 'required': ''}))
    customer_contact = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'input-sm form-control width-40', 'required': 'True'}))
    account_name = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'input-sm form-control width-40', 'required': 'True'}))


    class Meta:
        model = SalesforceData

        fields = ['opportunity_number', 'opportunity_name', 'value', 'estimate_start_date',
                  'estimate_end_date', 'planned_start_date', 'planned_end_date','customer_contact', 'account_name']
