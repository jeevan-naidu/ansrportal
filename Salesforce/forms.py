from django import forms


class UploadSalesforceDataForm(forms.Form):
    salesforce_data_file = forms.FileField(required=True, help_text="Please use semicolon delimited csv")
    salesforce_data_file.widget.attrs = {'class':'filestyle', 'data-buttonBefore':'true', 'data-iconName':'glyphicon glyphicon-paperclip'}