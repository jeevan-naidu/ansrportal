from django import forms


class UploadSalesforceDataForm(forms.Form):
    salesforce_data_file = forms.FileField()
    salesforce_data_file.widget.attrs = {'class':'filestyle', 'data-buttonBefore':'true', 'data-iconName':'glyphicon glyphicon-paperclip'}