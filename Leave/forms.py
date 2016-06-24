from models import LeaveApplications, LEAVE_TYPES_CHOICES
from django import forms
from bootstrap3_datetime.widgets import DateTimePicker
from django.utils.safestring import mark_safe
from django import forms
from django.contrib.auth.models import User
from Leave.models import LeaveApplications,  LEAVE_TYPES_CHOICES, SESSION_STATUS
from employee.models import Employee
import autocomplete_light
autocomplete_light.autodiscover()
LEAVE_TYPES_CHOICES = (('', '---------'),) + LEAVE_TYPES_CHOICES
SESSION_STATUS_CHOICES =(('', 'SELECT SESSION'),)+ SESSION_STATUS
dateTimeOption = {"format": "YYYY-MM-DD", "pickTime": False}


def LeaveForm(leavetype, data=None):
    class ApplyLeaveForm(forms.ModelForm):
        leave= forms.ChoiceField(choices=LEAVE_TYPES_CHOICES, initial= '............')
        leave.widget.attrs = {'class': 'form-control', 'required':'true'}
        class Meta:
            model = LeaveApplications

            fields = ['leave']

    class ApplyLeaveForm1(forms.ModelForm):
        leave_attachment = forms.FileField(label='Attachment', required=False, help_text=mark_safe("Allowed file types: jpg, csv, png, pdf, xls, xlsx, doc, docx, jpeg, eml.<br>Maximum allowed file size: 1MB"))
        # Add Bootstrap widgets
        leave_attachment.widget.attrs = {'class':'filestyle', 'data-buttonBefore':'true', 'data-iconName':'glyphicon glyphicon-paperclip'}

        leave= forms.ChoiceField(choices=LEAVE_TYPES_CHOICES, initial= leavetype)
        leave.widget.attrs = {'class': 'form-control', 'required':'true'}

        Reason = forms.CharField(max_length=100, required=False)
        # Add Bootstrap widgets
        Reason.widget.attrs = {'class': 'form-control'}

        fromDate = forms.DateField(
            label="From",
            widget=DateTimePicker(options=dateTimeOption),
        )
        fromDate.widget.attrs = {'class': 'form-control filter_class', 'required':'true'}

        class Meta:
            model = LeaveApplications

            fields = ['leave', 'fromDate', 'Reason', 'leave_attachment']
            widgets = {
              'Reason': forms.Textarea(attrs={ 'rows':8, 'cols':70}),
            }



    class ApplyLeaveForm2(forms.ModelForm):
        leave_attachment = forms.FileField(label='Attachment', required=False, help_text=mark_safe("Allowed file types: jpg, csv, png, pdf, xls, xlsx, doc, docx, jpeg, eml.<br>Maximum allowed file size: 1MB"))
        # Add Bootstrap widgets
        leave_attachment.widget.attrs = {'class':'filestyle', 'data-buttonBefore':'true', 'data-iconName':'glyphicon glyphicon-paperclip'}

        leave= forms.ChoiceField(choices=LEAVE_TYPES_CHOICES, initial= leavetype)
        leave.widget.attrs = {'class': 'form-control', 'required':'true'}

        Reason = forms.CharField(max_length=100, required=False)
        # Add Bootstrap widgets
        Reason.widget.attrs = {'class': 'form-control'}

        fromDate = forms.DateField(
            label="From",
            widget=DateTimePicker(options=dateTimeOption),
        )
        fromDate.widget.attrs = {'class': 'form-control filter_class', 'required':'true'}

        toDate = forms.DateField(
            label="To",
            widget=DateTimePicker(options=dateTimeOption),
        )
        toDate.widget.attrs = {'class': 'form-control filter_class', 'required':'false'}

        from_session= forms.ChoiceField(choices=SESSION_STATUS_CHOICES)
        from_session.widget.attrs = {'class': 'form-control', 'required':'false'}

        to_session= forms.ChoiceField(choices=SESSION_STATUS_CHOICES)
        to_session.widget.attrs = {'class': 'form-control', 'required':'false'}

        class Meta:
            model = LeaveApplications

            fields = ['leave', 'fromDate', 'from_session', 'toDate', 'to_session','Reason', 'leave_attachment']
            widgets = {
              'Reason': forms.Textarea(attrs={ 'rows':8, 'cols':70}),
              #'leave':forms.Select(attrs={'class': 'form-control', 'required':'true'}),
            #   'from_session':forms.Select(attrs={'class': 'form-control', 'required':'false'}),
            #   'to_session':forms.Select(attrs={'class': 'form-control', 'required':'false'}),
            }

    onetime_leave = ['maternity_leave', 'paternity_leave', 'bereavement_leave', 'comp_off_earned', 'comp_off_avail', 'pay_off']
    regular_leave = ['earned_leave', 'sick_leave', 'casual_leave', 'loss_of_pay', 'work_from_home', 'sabbatical']


    if leavetype in onetime_leave:
        if data:
            form = ApplyLeaveForm1(data)
            return form
        else:
            form = ApplyLeaveForm1()
            return form
    elif leavetype in regular_leave:
        if data:
            form = ApplyLeaveForm2(data)
            return form
        else:
            form = ApplyLeaveForm2()
            return form
    else:
        form = ApplyLeaveForm()
        return form

dateTimeOption = {"format": "YYYY-MM-DD", "pickTime": False}


class LeaveListViewForm(autocomplete_light.ModelForm):

    # user = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True),
    #                               widget=autocomplete_light.ChoiceWidget('UserAutocompleteUser'))
    #
    # user.widget.attrs = {'class': 'form-control filter_class', 'placeholder': 'Enter Employee Name'}

    # apply_to = forms.ModelChoiceField(queryset=Employee.objects.exclude(manager__user__first_name__isnull=True).
    #                                   values_list('manager__user__username',
    #                                               flat=True).distinct().order_by('manager__user__username'),
    #                                   empty_label="---------")

    # apply_to.widget.attrs = {'class': 'form-control filter_class'}

    leave_type = forms.ChoiceField(choices=LEAVE_TYPES_CHOICES)

    leave_type.widget.attrs = {'class': 'form-control filter_class'}

    from_date = forms.DateField(
        label="From",
        widget=DateTimePicker(options=dateTimeOption),
    )
    from_date.widget.attrs = {'class': 'form-control filter_class input-sm'}

    to_date = forms.DateField(
        label="To",
        widget=DateTimePicker(options=dateTimeOption),
    )
    to_date.widget.attrs = {'class': 'form-control filter_class input-sm'}

    class Meta:
        model = LeaveApplications
        # fields = ['leave_type', 'from_date', 'to_date', 'status']
        fields = ['leave_type', 'from_date', 'to_date', 'status']
        # fields = (
        #     'user',
        # )
