from django import forms
from django.contrib.auth.models import User
from models import Profile, MRF, RESULT_STATUS, GENDER_CHOICES, REFERENCE_SOURCE, Position
from employee.models import Employee
from bootstrap3_datetime.widgets import DateTimePicker
import autocomplete_light
autocomplete_light.autodiscover()
dateTimeOption = {"format": "YYYY-MM-DD", "pickTime": False}

class ProfileForm(autocomplete_light.ModelForm):
    candidate_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-50'}))
    mobile_number = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'width-50'}))
    email_id = forms.EmailField(widget=forms.TextInput(attrs={'class': 'width-50'}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    date_of_birth = forms.DateField(widget=DateTimePicker(options=dateTimeOption),)
    date_of_birth.widget.attrs = {'class': 'no-bd', 'required': 'true'}

    source = forms.ChoiceField(choices=REFERENCE_SOURCE)
    source.widget.attrs = {'class': 'width-40', 'required': 'true'}
    refered_by = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True),
                                  widget=autocomplete_light.ChoiceWidget('UserAutocompleteUserHireSearch'))

    refered_by.widget.attrs = {'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Employee Name'}
    candidate_status = forms.ChoiceField(choices=RESULT_STATUS)
    requisition_number = forms.ModelChoiceField(queryset=MRF.objects.all(),
                                        widget=autocomplete_light.ChoiceWidget('MRFAutoCompleteRequisitionSearch'))

    requisition_number.widget.attrs = {'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Employee Name'}
    department = forms.ChoiceField()
    designation = forms.ChoiceField()
    specialization = forms.ChoiceField()
    manager = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True),
                                        widget=autocomplete_light.ChoiceWidget('UserAutocompleteUserHireSearch'))

    manager.widget.attrs = {'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Manager Name'}
    count = forms.CharField(max_length=10)

    interview_by = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True),
                                     widget=autocomplete_light.ChoiceWidget('UserAutocompleteUserHireSearch'))

    interview_by.widget.attrs = {'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Manager Name'}
    interview_step = forms.ChoiceField()
    interview_on = forms.DateField()
    interview_status = forms.ChoiceField()
    remark = forms.CharField(max_length=100)

    class Meta:
        model = Profile
        fields = ['candidate_name', 'mobile_number', 'email_id', 'gender', 'date_of_birth', 'source', 'refered_by',
                  'candidate_status', 'requisition_number', 'department', 'designation', 'specialization',
                  'manager', 'count', 'interview_by', 'interview_step', 'interview_on', 'interview_status', 'remark']


class MRFForm(autocomplete_light.ModelForm):
    requisition_number = forms.ModelChoiceField(queryset=MRF.objects.all(),
                                        widget=autocomplete_light.ChoiceWidget('MRFAutoCompleteRequisitionSearch'))

    requisition_number.widget.attrs = {'class': 'width-50', 'placeholder': 'Enter requisition number'}
    department = forms.ChoiceField(choices=[(dep.department, dep.department) for dep in Position.objects.all()])
    department.widget.attrs = {'class': 'width-40', 'required': 'true'}
    designation = forms.ChoiceField()
    designation.widget.attrs = {'class': 'width-40', 'required': 'true'}
    specialization = forms.ChoiceField()
    specialization.widget.attrs = {'class': 'width-40', 'required': 'true'}
    manager = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True),
                                        widget=autocomplete_light.ChoiceWidget('UserAutocompleteUserHireSearch'))

    manager.widget.attrs = {'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Manager Name'}
    count = forms.CharField(max_length=10)

    class Meta:
        model = MRF
        fields = ['requisition_number', 'department', 'designation', 'specialization', 'manager', 'count']


