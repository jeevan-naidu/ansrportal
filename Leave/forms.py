

from models import LeaveApplications, LEAVE_TYPES_CHOICES
from django import forms
from bootstrap3_datetime.widgets import DateTimePicker
from django.forms import TextInput
from django.utils.safestring import mark_safe
from django import forms
from django.contrib.auth.models import User
from Leave.models import LeaveApplications, ShortAttendance, LEAVE_TYPES_CHOICES, LEAVE_TYPES_CHOICES_LEAVES, LEAVE_TYPES_CHOICES_NON_LEAVES, SESSION_STATUS, LeaveSummary
from employee.models import Employee
from django.contrib.auth.models import User
from datetime import date, time
from dal import autocomplete


LEAVE_TYPES_CHOICES = (('', '---------'),) + LEAVE_TYPES_CHOICES
LEAVE_TYPES_CHOICES_LEAVES = (('', '---------'),) + LEAVE_TYPES_CHOICES_LEAVES
LEAVE_TYPES_CHOICES_NON_LEAVES = (('', '---------'),) + LEAVE_TYPES_CHOICES_NON_LEAVES

SESSION_STATUS_CHOICES = (('', 'SELECT SESSION'),) + SESSION_STATUS
dateTimeOption = {"format": "YYYY-MM-DD", "pickTime": False}


class UserListViewForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(url='AutocompleteUserSearch', attrs={
            'data-placeholder': 'Type  Your Team Member Name ...',
        }, ),
        required=True, )
    class Meta:
        model = User
        fields = ['user']

def LeaveForm(leavetype, user, leave_type_leave, data=None):
    if leave_type_leave == "1":
        print leave_type_leave, 101010
        LEAVE_TYPES_CHOICES = LEAVE_TYPES_CHOICES_LEAVES
    elif leave_type_leave == "2":
        print leave_type_leave, 202020
        LEAVE_TYPES_CHOICES = LEAVE_TYPES_CHOICES_NON_LEAVES
    else:
        print leave_type_leave, 303030


    class ApplyLeaveForm(forms.ModelForm):
        leave= forms.ChoiceField(choices=LEAVE_TYPES_CHOICES, initial= '............')
        leave.widget.attrs = {'class': 'form-control', 'required':'true'}
        name = forms.CharField(initial = user, widget=forms.HiddenInput())
        class Meta:
            model = LeaveApplications

            fields = ['leave','name']

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
        name = forms.CharField(initial = user, widget=forms.HiddenInput())
        class Meta:
            model = LeaveApplications

            fields = ['leave', 'fromDate', 'Reason', 'leave_attachment','name']
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

        name = forms.CharField(initial = user, widget=forms.HiddenInput())

        class Meta:
            model = LeaveApplications

            fields = ['leave', 'fromDate', 'from_session', 'toDate', 'to_session','Reason', 'leave_attachment','name']
            widgets = {
              'Reason': forms.Textarea(attrs={'rows': 8, 'cols': 70}),
            }

    class ApplyLeaveForm3(forms.ModelForm):
        leave_attachment = forms.FileField(label='Attachment', required=False, help_text=mark_safe("Allowed file types: jpg, csv, png, pdf, xls, xlsx, doc, docx, jpeg, eml.<br>Maximum allowed file size: 1MB"))
        # Add Bootstrap widgets
        leave_attachment.widget.attrs = {'class':'filestyle', 'data-buttonBefore':'true', 'data-iconName':'glyphicon glyphicon-paperclip'}

        leave= forms.ChoiceField(choices=LEAVE_TYPES_CHOICES, initial= leavetype)
        leave.widget.attrs = {'class': 'form-control', 'required':'true'}

        Reason = forms.CharField(max_length=100, required=False)
        # Add Bootstrap widgets
        Reason.widget.attrs = {'class': 'form-control'}

        hours = forms.RegexField(max_length=4, required=True ,regex=r'^[0-9]{4}$', help_text='Hours format(hhmm), example:0430',
                                widget=TextInput(attrs={'type': 'number', 'pattern': '^[0-9]{4}$'}))
        # Add Bootstrap widgets
        hours.widget.attrs = {'class': 'form-control'}

        from_session = forms.ChoiceField(choices=SESSION_STATUS_CHOICES)
        from_session.widget.attrs = {'class': 'form-control', 'required': 'false'}

        to_session = forms.ChoiceField(choices=SESSION_STATUS_CHOICES)
        to_session.widget.attrs = {'class': 'form-control', 'required': 'false'}

        fromDate = forms.DateField(
            label="From",
            widget=DateTimePicker(options=dateTimeOption),
        )
        fromDate.widget.attrs = {'class': 'form-control filter_class', 'required': 'true'}

        toDate = forms.DateField(
            label="To",
            widget=DateTimePicker(options=dateTimeOption),
        )
        toDate.widget.attrs = {'class': 'form-control filter_class', 'required': 'false'}
        name = forms.CharField(initial = user, widget=forms.HiddenInput())
        class Meta:
            model = LeaveApplications

            fields = ['leave', 'fromDate', 'from_session', 'toDate', 'to_session', 'Reason', 'hours', 'leave_attachment','name']
            widgets = {
              'Reason': forms.Textarea(attrs={ 'rows':8, 'cols':70}),
            }


    class ApplyLeaveForm4(forms.ModelForm):

        leave= forms.ChoiceField(choices=LEAVE_TYPES_CHOICES, initial= leavetype)
        leave.widget.attrs = {'class': 'form-control', 'required':'true'}

        Reason = forms.CharField(max_length=100, required=False)
        # Add Bootstrap widgets
        Reason.widget.attrs = {'class': 'form-control'}

        fromDate = forms.DateField(
            label="Date",
            widget=DateTimePicker(options=dateTimeOption),
        )
        fromDate.widget.attrs = {'class': 'form-control filter_class', 'required': 'true'}

        temp_id = forms.RegexField(max_length=2, required=True ,regex=r'^[0-9]{2}$', help_text='Enter 2 digit temporary ID number',
                                widget=TextInput(attrs={'type': 'number', 'pattern': '^[0-9]{2}$'}))
        # Add Bootstrap widgets
        temp_id.widget.attrs = {'class': 'form-control'}

        name = forms.CharField(initial = user, widget=forms.HiddenInput())

        class Meta:
            model = LeaveApplications

            fields = ['leave', 'fromDate', 'Reason', 'temp_id', 'name']
            widgets = {
              'Reason': forms.Textarea(attrs={'rows': 8, 'cols': 70}),
            }

    onetime_leave = ['maternity_leave',
                     'paternity_leave',
                     'comp_off_avail',
                     'pay_off',
                     'short_leave',
                     'comp_off_earned']
    regular_leave = ['earned_leave',
                     'sick_leave',
                     'bereavement_leave',
                     'casual_leave',
                     'loss_of_pay',
                     'sabbatical',
                     'ooo_dom',
                     'ooo_int']
    work_from_home = ['work_from_home']
    temp_id = ['temp_id']

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
    elif leavetype in work_from_home:
        if data:
            form = ApplyLeaveForm3(data)
            return form
        else:
            form = ApplyLeaveForm3()
            return form
    elif leavetype in temp_id:
        if data:
            form = ApplyLeaveForm4(data)
            return form
        else:
            form = ApplyLeaveForm4()
            return form
    else:
        form = ApplyLeaveForm()
        return form

dateTimeOption = {"format": "YYYY-MM-DD", "pickTime": False}



def ShortLeaveForm(leavetype, user,fordate=None,leaveid=None, data=None):
    if fordate:
        leave_applied_date = fordate.year
    else:
        leave_applied_date = date.today().year
    staytime = ShortAttendance.objects.get(id=leaveid)
    SHORT_LEAVE_TYPES_CHOICES = ( ('loss_of_pay', 'Loss Of Pay'),)
    leaveallowed = {'earned_leave':'Earned Leave', 'sick_leave':'Sick Leave', 'casual_leave':'Casual Leave','short_leave':'Short Leave', 'comp_off_avail':'Comp Off Avail'}
    leaveAvaliable = LeaveSummary.objects.filter(user=user, leave_type__in =[1,2,3,13], year=leave_applied_date).values('balance','leave_type__leave_type')
    for leave in leaveAvaliable:
        if leave['leave_type__leave_type'] != 'short_leave' and float(leave['balance']) > 0:
            SHORT_LEAVE_TYPES_CHOICES = ((leave['leave_type__leave_type'],
                                          leaveallowed[leave['leave_type__leave_type']] ),)+SHORT_LEAVE_TYPES_CHOICES
        elif float(leave['balance']) > 0 and staytime.stay_time > time(07,00,00):
            SHORT_LEAVE_TYPES_CHOICES = ((leave['leave_type__leave_type'],
                                          leaveallowed[leave['leave_type__leave_type']]),) + SHORT_LEAVE_TYPES_CHOICES
    SHORT_LEAVE_TYPES_CHOICES = (('', '---------'),) + SHORT_LEAVE_TYPES_CHOICES

    class ApplyShortLeaveForm(forms.ModelForm):
        leave = forms.ChoiceField(choices=SHORT_LEAVE_TYPES_CHOICES, initial=leavetype)
        leave.widget.attrs = {'class': 'form-control', 'required': 'true'}

        Reason = forms.CharField(max_length=100, required=False)
        Reason.widget.attrs = {'class': 'form-control'}

        fromDate = forms.DateField(
            initial=fordate,
            label="From",
            widget=DateTimePicker(options=dateTimeOption),
        )
        fromDate.widget.attrs = {'class': 'form-control filter_class', 'required': 'true', 'readonly':'readonly'}

        toDate = forms.DateField(
            initial=fordate,
            label="To",
            widget=DateTimePicker(options=dateTimeOption),
        )
        toDate.widget.attrs = {'class': 'form-control filter_class', 'required': 'false', 'readonly':'readonly'}

        from_session = forms.ChoiceField(choices=SESSION_STATUS_CHOICES)
        from_session.widget.attrs = {'class': 'form-control', 'required': 'false'}

        to_session = forms.ChoiceField(choices=SESSION_STATUS_CHOICES)
        to_session.widget.attrs = {'class': 'form-control', 'required': 'false'}

        name = forms.CharField(initial=user, widget=forms.HiddenInput())
        leave_id = forms.CharField(initial=leaveid, widget=forms.HiddenInput())

        class Meta:
            model = LeaveApplications
            fields = ['leave', 'fromDate', 'from_session', 'toDate', 'to_session', 'Reason', 'name','id']
            widgets = {
                'Reason': forms.Textarea(attrs={'rows': 8, 'cols': 70}),

            }
    class ApplyShortLeaveForm1(forms.ModelForm):
        leave = forms.ChoiceField(choices=SHORT_LEAVE_TYPES_CHOICES, initial=leavetype)
        leave.widget.attrs = {'class': 'form-control', 'required': 'true'}

        Reason = forms.CharField(max_length=100, required=False)
        Reason.widget.attrs = {'class': 'form-control'}

        fromDate = forms.DateField(
            initial=fordate,
            label="From",
            widget=DateTimePicker(options=dateTimeOption),
        )
        fromDate.widget.attrs = {'class': 'form-control filter_class', 'required': 'true', 'readonly':'readonly'}

        name = forms.CharField(initial=user, widget=forms.HiddenInput())
        leave_id = forms.CharField(initial=leaveid, widget=forms.HiddenInput())

        class Meta:
            model = LeaveApplications
            fields = ['leave', 'fromDate', 'Reason', 'name','id']
            widgets = {
                'Reason': forms.Textarea(attrs={'rows': 8, 'cols': 70}),

            }

    if leavetype in ['short_leave']:
        if data:
            form = ApplyShortLeaveForm1(data)
            return form
        else:
            form = ApplyShortLeaveForm1()
            return form
    else:
        if data:
            form = ApplyShortLeaveForm(data)
            return form
        else:
            form = ApplyShortLeaveForm()
            return form


class LeaveListViewForm(forms.ModelForm):
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


class ShortAttendanceRemarkForm(forms.ModelForm):
    Reason = forms.CharField(label="Remark", widget=forms.Textarea, max_length=500, required=True)
    Reason.widget.attrs = {'class': 'form-control'}
    leave_id = forms.CharField(widget=forms.HiddenInput())
    fordate = forms.DateField(
        label="For Date",
        widget=DateTimePicker(options=dateTimeOption),
    )
    fordate.widget.attrs = {'class': 'form-control filter_class', 'required': 'true', 'readonly': 'readonly'}


    class Meta:
        model = ShortAttendance
        fields = ['fordate', 'leave_id', 'Reason']


