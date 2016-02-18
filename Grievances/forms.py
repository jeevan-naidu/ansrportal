from models import Grievances, SATISFACTION_CHOICES, Grievances_catagory
#
#import ipdb;ipdb.set_trace()
#GRIEVANCE_CATAGORIES = () + GRIEVANCE_CATAGORIES
'jpg', 'csv','png', 'pdf', 'xlsx', 'docx', 'doc', 'jpeg'
from django import forms
class AddGrievanceForm(forms.ModelForm):
    grievance_attachment = forms.FileField(label='Attachment', required=False, help_text="Allowed file types: jpg, csv, png, pdf, xls, xlsx, doc, docx, jpeg")
    # Add Bootstrap widgets
    grievance_attachment.widget.attrs = {'class':'filestyle', 'data-buttonBefore':'true', 'data-iconName':'glyphicon glyphicon-paperclip'}
    
    catagory = forms.ModelChoiceField(queryset=Grievances_catagory.objects.filter(active=True), empty_label="---------")
    # Add Bootstrap widgets
    catagory.widget.attrs = {'class': 'form-control'}
    
    subject = forms.CharField(max_length=100)
    # Add Bootstrap widgets
    subject.widget.attrs = {'class': 'form-control'}
    
    class Meta:
        model = Grievances
        fields = ['catagory', 'subject', 'grievance', 'grievance_attachment']
        
        widgets = {
          'grievance': forms.Textarea(attrs={'rows':12, 'cols':80}),
        }
        

