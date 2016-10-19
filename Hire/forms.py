from django import forms
from django.contrib.auth.models import User
from models import Profile, Count, GENDER_CHOICES, REFERENCE_SOURCE, Position, MRF, Process,INTERVIEW_PROCESS
from bootstrap3_datetime.widgets import DateTimePicker
from dal import autocomplete

dateTimeOption = {"format": "YYYY-MM-DD", "pickTime": False}
DEPARTMENT = (('','........'),) + tuple([(dep['department'], dep['department']) for dep in Position.objects.filter().values('department').distinct()])
RESULT_STATUS = (('rejected', 'Rejected'), ('selected', 'Selected'))
class ProfileForm(forms.ModelForm):
    candidate_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-50 input-sm form-control',
                                                                                  'required': '', 'data-error': 'Please enter candidate name'}))
    mobile_number = forms.RegexField(regex=r'^\+?1?\d{9,15}$',
                                   error_message=(
                                       "Phone number must be entered in the format: '+999999999'. "
                                       "Up to 15 digits allowed."),
                                   widget=forms.TextInput(attrs={'class': 'width-30 input-sm form-control',
                                                                 'required': 'true','type': 'tel', 'pattern':'^\+?1?\d{9,15}$'}))

    email_id = forms.EmailField(widget=forms.TextInput(attrs={'class': 'width-50 input-sm', 'type':'email'}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.RadioSelect({'class': '', 'required': 'true'}))
    date_of_birth = forms.DateField(widget=DateTimePicker(options=dateTimeOption),)
    date_of_birth.widget.attrs = {'class': 'input-sm form-control filter_class', 'required': 'true'}
    source = forms.ChoiceField(choices=REFERENCE_SOURCE)
    source.widget.attrs = {'class': 'width-40', 'required': 'true'}
    refered_by = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2(url='hire_user_search', attrs={
            'data-placeholder': 'Type Member Name ...',
        }, ), )
    refered_by.widget.attrs = {'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Employee Name'
                               }
    requisition_number = forms.ModelChoiceField(
        queryset=Count.objects.all(),
        required=True,
        widget=autocomplete.ModelSelect2(url='hire_requsition_based_on_user', attrs={
            'data-placeholder': 'Type Requisition Number ...',
        }, ), )

    requisition_number.widget.attrs = {'class': 'form-control filter_class input-sm',
                                       'placeholder': 'Enter Requisition number'}
    department = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-100 input-sm form-control',
                                                                              'required': 'true'}))
    designation = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-100 input-sm form-control',
                                                                               'required': 'true'}))
    specialization = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-100 input-sm form-control',
                                                                                  'required': 'true'}))
    manager = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-100 input-sm',
                                                                           'required': 'true'}))

    manager.widget.attrs = {'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Manager Name'}
    # interview_by = forms.ModelChoiceField()
    interview_by = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        widget=autocomplete.ModelSelect2(url='hire_user_search', attrs={
            'data-placeholder': 'Type Member Name ...',
        }, ), )
    interview_by.widget.attrs = { 'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Interviewer Name',
                                }
    interview_on = forms.DateField(widget=DateTimePicker(options=dateTimeOption), )
    interview_on.widget.attrs = {'class': 'input-sm form-control filter_class', 'required': 'true'}
    interview_status = forms.ChoiceField(choices=RESULT_STATUS)
    interview_status.widget.attrs = {'class': 'width-40', 'required': 'true'}
    remark = forms.CharField(max_length=100, required=False)
    remark.widget.attrs = {'class': 'width-50 input-sm'}

    class Meta:
        model = Profile
        fields = ['candidate_name', 'mobile_number', 'email_id', 'gender', 'date_of_birth', 'source', 'refered_by',
                  'requisition_number', 'department', 'designation', 'specialization',
                  'manager', 'interview_by', 'interview_on', 'interview_status', 'remark']




class MRFForm(forms.ModelForm):
    requisition_number = forms.ModelChoiceField(
        queryset=MRF.objects.all(),
        required=True,
        widget=autocomplete.ModelSelect2(url='hire_requsition_based_on_user', attrs={
            'data-placeholder': 'Type MRF Number ...',
        }, ), )

    requisition_number.widget.attrs = {'class': 'form-control filter_class input-sm',
                                       'placeholder': 'Enter Requisition number'}
    department = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-50 input-sm'}))
    designation = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-50 input-sm'}))

    specialization = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-50 input-sm'}))
    raised_by = forms.CharField(max_length=50)

    raised_by.widget.attrs = {'class': 'form-control filter_class input-sm width-50', 'placeholder': 'Enter Manager Name'}
    count = forms.CharField(max_length=10, widget=forms.TextInput(
        attrs={'class': 'width-50 input-sm', 'required': 'true','type':'number','min':'0'}))

    class Meta:
        model = MRF
        fields = ['requisition_number', 'department', 'designation', 'specialization', 'raised_by', 'count']


class NewMRFForm(forms.ModelForm):
    requisition_number = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'width-50 input-sm', 'required': 'true'}))
    department = forms.ChoiceField(initial='.....', choices=DEPARTMENT)
    department.widget.attrs = {'class': 'width-40', 'required': 'true'}
    designation = forms.ChoiceField(choices=[(dep['designation'], dep['designation'])
                                             for dep in Position.objects.filter().values('designation').distinct()])
    designation.widget.attrs = {'class': 'width-40', 'required': 'true'}
    specialization = forms.ChoiceField(choices=[(dep['specialization'], dep['specialization'])
                                                for dep in Position.objects.filter().values('specialization').distinct()])
    specialization.widget.attrs = {'class': 'width-40', 'required': 'true'}
    manager = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        widget=autocomplete.ModelSelect2(url='hire_user_search', attrs={
            'data-placeholder': 'Type Manaager Name ...',
        }, ), )


    # manager.widget.attrs = {'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Manger Name',
    #                            }
    count = forms.CharField(max_length=10, widget=forms.TextInput(
        attrs={'class': 'width-50 input-sm', 'required': 'true', 'type': 'number', 'min':'0'}))

    class Meta:
        model = MRF
        fields = ['requisition_number', 'department', 'designation', 'specialization', 'manager', 'count']


class ProcessForm(forms.ModelForm):
    profile_id = forms.CharField(widget=forms.HiddenInput())
    interview_by = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        widget=autocomplete.ModelSelect2(url='hire_user_search', attrs={
            'data-placeholder': 'Type Interviewer Name ...',
        }, ), )

    interview_by.widget.attrs = {'class': 'form-control filter_class input-sm', 'placeholder': 'Enter Manager Name'}
    interview_on = forms.DateField(widget=DateTimePicker(options=dateTimeOption), )
    interview_on.widget.attrs = {'class': 'input-sm form-control filter_class', 'required': 'true'}
    interview_status = forms.ChoiceField(choices=RESULT_STATUS)
    interview_status.widget.attrs = {'class': 'width-40', 'required': 'true'}
    remark = forms.CharField(max_length=100, required=False)
    remark.widget.attrs = {'class': 'width-50 input-sm'}

    class Meta:
        model = Process
        fields = ['profile_id', 'interview_by', 'interview_on', 'interview_status', 'remark']