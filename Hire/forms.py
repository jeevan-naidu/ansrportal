from django import forms
from django.contrib.auth.models import User
from models import Profile, Count, RESULT_STATUS, GENDER_CHOICES, REFERENCE_SOURCE, Position, INTERVIEW_PROCESS, MRF, Process
from employee.models import Employee
from bootstrap3_datetime.widgets import DateTimePicker
import autocomplete_light
autocomplete_light.autodiscover()
dateTimeOption = {"format": "YYYY-MM-DD", "pickTime": False}


class ProfileForm(autocomplete_light.ModelForm):
    candidate_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-50 input-sm'}))
    mobile_number = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-30 input-sm'}))
    email_id = forms.EmailField(widget=forms.TextInput(attrs={'class': 'width-50 input-sm'}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.RadioSelect({'class': ''}))
    date_of_birth = forms.DateField(widget=DateTimePicker(options=dateTimeOption),)
    date_of_birth.widget.attrs = {'class': 'no-bd, input-sm form-control filter_class', 'required': 'true'}
    source = forms.ChoiceField(choices=REFERENCE_SOURCE)
    source.widget.attrs = {'class': 'width-40', 'required': 'true'}
    refered_by = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True),required=False,
                                  widget=autocomplete_light.ChoiceWidget('UserAutocompleteUserHireSearch'))

    refered_by.widget.attrs = {'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Employee Name',
                               }
    requisition_number = forms.ModelChoiceField(queryset=Count.objects.all(),
                                        widget=autocomplete_light.ChoiceWidget('CountAutoCompleteRequisitionSearch'))

    requisition_number.widget.attrs = {'class': 'form-control filter_class input-sm',
                                       'placeholder': 'Enter Requsition number'}
    department = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-100 input-sm'}))
    designation = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-100 input-sm'}))
    specialization = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-100 input-sm'}))
    manager = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-100 input-sm'}))

    manager.widget.attrs = {'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Manager Name'}

    interview_by = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True),
                                     widget=autocomplete_light.ChoiceWidget('UserAutocompleteUserHireSearch'))

    interview_by.widget.attrs = {'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Manager Name'}
    # interview_step = forms.ChoiceField(choices=INTERVIEW_PROCESS)
    # interview_step.widget.attrs = {'class': 'width-40', 'required': 'true'}
    interview_on = forms.DateField(widget=DateTimePicker(options=dateTimeOption), )
    interview_on.widget.attrs = {'class': 'no-bd, input-sm form-control filter_class', 'required': 'true'}
    interview_status = forms.ChoiceField(choices=RESULT_STATUS)
    interview_status.widget.attrs = {'class': 'width-40', 'required': 'true'}
    remark = forms.CharField(max_length=100)
    remark.widget.attrs = {'class': 'width-50', 'required': 'true'}

    class Meta:
        model = Profile
        fields = ['candidate_name', 'mobile_number', 'email_id', 'gender', 'date_of_birth', 'source', 'refered_by',
                  'requisition_number', 'department', 'designation', 'specialization',
                  'manager', 'interview_by', 'interview_on', 'interview_status', 'remark']



class MRFForm(autocomplete_light.ModelForm):
    requisition_number = forms.ModelChoiceField(queryset=MRF.objects.all(),
                                                widget=autocomplete_light.ChoiceWidget(
                                                    'MRFAutoCompleteRequisitionSearch'))

    requisition_number.widget.attrs = {'class': 'form-control filter_class input-sm',
                                       'placeholder': 'Enter Requsition number'}
    department = forms.ChoiceField(initial='.........',choices=[(dep['department'], dep['department'])
                                                                for dep in Position.objects.filter().values('department').distinct()])
    department.widget.attrs = {'class': 'width-40', 'required': 'true'}
    designation = forms.ChoiceField(choices=[(dep['designation'], dep['designation'])
                                             for dep in Position.objects.filter().values('designation').distinct()])
    designation.widget.attrs = {'class': 'width-40', 'required': 'true'}
    specialization = forms.ChoiceField(choices=[(dep['specialization'], dep['specialization'])
                                                for dep in Position.objects.filter().values('specialization').distinct()])
    specialization.widget.attrs = {'class': 'width-40', 'required': 'true'}
    raised_by = forms.CharField(max_length=50)

    raised_by.widget.attrs = {'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Manager Name'}
    count = forms.CharField(max_length=10)
    count.widget.attrs = {'class': 'width-50', 'required': 'true'}

    class Meta:
        model = MRF
        fields = ['requisition_number', 'department', 'designation', 'specialization', 'raised_by', 'count']


class NewMRFForm(autocomplete_light.ModelForm):
    requisition_number = forms.CharField(max_length=100)

    requisition_number.widget.attrs = {'class': 'form-control filter_class input-sm',
                                       'placeholder': 'Enter Requsition number'}
    department = forms.ChoiceField(initial='.....',choices=[(dep['department'], dep['department'])
                                                                for dep in Position.objects.filter().values('department').distinct()])
    department.widget.attrs = {'class': 'width-40', 'required': 'true'}
    designation = forms.ChoiceField(choices=[(dep['designation'], dep['designation'])
                                             for dep in Position.objects.filter().values('designation').distinct()])
    designation.widget.attrs = {'class': 'width-40', 'required': 'true'}
    specialization = forms.ChoiceField(choices=[(dep['specialization'], dep['specialization'])
                                                for dep in Position.objects.filter().values('specialization').distinct()])
    specialization.widget.attrs = {'class': 'width-40', 'required': 'true'}
    manager = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True),
                                        widget=autocomplete_light.ChoiceWidget('UserAutocompleteUserHireSearch'))

    manager.widget.attrs = {'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Manager Name'}
    count = forms.CharField(max_length=10)
    count.widget.attrs = {'class': 'width-50', 'required': 'true'}

    class Meta:
        model = MRF
        fields = ['requisition_number', 'department', 'designation', 'specialization', 'manager', 'count']


class ProcessForm(autocomplete_light.ModelForm):
    interview_by = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True),
                                     widget=autocomplete_light.ChoiceWidget('UserAutocompleteUserHireSearch'))

    interview_by.widget.attrs = {'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Manager Name'}
    interview_step = forms.ChoiceField(choices=INTERVIEW_PROCESS)
    interview_step.widget.attrs = {'class': 'width-40', 'required': 'true'}
    interview_on = forms.DateField(widget=DateTimePicker(options=dateTimeOption), )
    interview_on.widget.attrs = {'class': 'no-bd, input-sm form-control filter_class', 'required': 'true'}
    interview_status = forms.ChoiceField(choices=RESULT_STATUS)
    interview_status.widget.attrs = {'class': 'width-40', 'required': 'true'}
    remark = forms.CharField(max_length=100)
    remark.widget.attrs = {'class': 'width-50', 'required': 'true'}

    class Meta:
        model = Process
