from models import Grievances, SATISFACTION_CHOICES, Grievances_category
from django.utils.safestring import mark_safe

from django import forms
class AddGrievanceForm(forms.ModelForm):
    grievance_attachment = forms.FileField(label='Attachment', required=False, help_text=mark_safe("Allowed file types: jpg, csv, png, pdf, xls, xlsx, doc, docx, jpeg.<br>Maximum allowed file size: 1MB"))
    # Add Bootstrap widgets
    grievance_attachment.widget.attrs = {'class':'filestyle', 'data-buttonBefore':'true', 'data-iconName':'glyphicon glyphicon-paperclip'}
    
    category = forms.ModelChoiceField(queryset=Grievances_category.objects.filter(active=True), empty_label="---------")
    # Add Bootstrap widgets
    category.widget.attrs = {'class': 'form-control', 'required':'true'}
    
    subject = forms.CharField(max_length=100)
    # Add Bootstrap widgets
    subject.widget.attrs = {'class': 'form-control', 'required':'true', 'maxlength':'100', 'placeholder':'Max 100 characters'}
    
    class Meta:
        model = Grievances
        fields = ['category', 'subject', 'grievance', 'grievance_attachment']
        
        widgets = {
          'grievance': forms.Textarea(attrs={'class': 'form-control', 'rows':8, 'cols':70, 'required':'true','placeholder':'Max 2000 characters'}),
        }

    
    def clean(self):
        '''  Custom clean method. Validations for spaces for input fields '''
        
        if self.cleaned_data.get('subject', ''):
            self.cleaned_data['subject'] = self.cleaned_data['subject'].strip()
        if self.cleaned_data.get('grievance', ''):
            self.cleaned_data['grievance'] = self.cleaned_data['grievance'].strip()
        
        return self.cleaned_data
