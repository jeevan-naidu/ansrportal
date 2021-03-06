from django.db.models import Q
from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from MyANSRSource.models import Book, Project, ProjectTeamMember, \
    ProjectMilestone, Chapter, ProjectChangeInfo, Activity, Task, \
    projectType, ProjectManager, TimeSheetEntry, BTGReport
from bootstrap3_datetime.widgets import DateTimePicker
from CompanyMaster.models import OfficeLocation, BusinessUnit, Customer
from employee.models import Remainder
import datetime
import calendar
import helper
from dal import autocomplete

dateTimeOption = {"format": "YYYY-MM-DD", "pickTime": False}
startDate = TimeSheetEntry.objects.all().values('wkstart').distinct()
year = list(set([eachDate['wkstart'].year for eachDate in startDate]))
MONTHS = tuple(zip(
    range(1, 13),
    (calendar.month_name[i] for i in range(1, 13))
))
YEARS = tuple(zip(year, year))


class ActivityForm(forms.Form):
    activity = forms.ModelChoiceField(
        queryset=Activity.objects.filter(active=True).order_by('name'),
        label="Activity",
        required=False,
    )
    activity_monday = forms.DecimalField(label="Mon",
                                         max_digits=12,
                                         min_value=0.0,
                                         max_value=24.0,
                                         decimal_places=2,
                                         )
    activity_tuesday = forms.DecimalField(label="Tue",
                                          max_digits=12,
                                          min_value=0.0,
                                          max_value=24.0,
                                          decimal_places=2,
                                          )
    activity_wednesday = forms.DecimalField(label="Wed",
                                            max_digits=12,
                                            min_value=0.0,
                                            max_value=24.0,
                                            decimal_places=2,
                                            )
    activity_thursday = forms.DecimalField(label="Thu",
                                           max_digits=12,
                                           min_value=0.0,
                                           max_value=24.0,
                                           decimal_places=2,
                                           )
    activity_friday = forms.DecimalField(label="Fri",
                                         max_digits=12,
                                         min_value=0.0,
                                         max_value=24.0,
                                         decimal_places=2,
                                         )
    activity_saturday = forms.DecimalField(label="Sat",
                                           max_digits=12,
                                           min_value=0.0,
                                           max_value=24.0,
                                           decimal_places=2,
                                           )
    activity_sunday = forms.DecimalField(label="Sun",
                                         max_digits=12,
                                         min_value=0.0,
                                         max_value=24.0,
                                         decimal_places=2,
                                         )
    activity_total = forms.DecimalField(label="Total",
                                        max_digits=12,
                                        min_value=0.0,
                                        decimal_places=2,
                                        )

    atId = forms.IntegerField(label="id",
                              required=False,
                              widget=forms.HiddenInput())
    approved = forms.BooleanField(label="approved",
                                  required=False)
    hold = forms.BooleanField(label="hold",
                              required=False)

    def __init__(self, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)
        self.fields['activity_total'].widget.attrs['readonly'] = 'True'
        self.fields['activity'].widget.attrs['class'] = "form-control"
        self.fields['activity_monday'].widget.attrs['class'] = "form-control \
        days input-field Mon-t hrcheck"
        self.fields['activity_tuesday'].widget.attrs['class'] = "form-control \
        days input-field Tue-t hrcheck"
        self.fields['activity_wednesday'].widget.attrs['class'] = "form-control \
        days input-field Wed-t hrcheck"
        self.fields['activity_thursday'].widget.attrs['class'] = "form-control \
        days input-field Thu-t hrcheck"
        self.fields['activity_friday'].widget.attrs['class'] = "form-control \
        days input-field Fri-t hrcheck"
        self.fields['activity_saturday'].widget.attrs['class'] = "form-control \
        days input-field Sat-t hrcheck"
        self.fields['activity_sunday'].widget.attrs['class'] = "form-control \
        days input-field Sun-t hrcheck"
        self.fields['activity_total'].widget.attrs['class'] = "form-control \
        total input-field r-total"
        self.fields['activity_monday'].widget.attrs['value'] = 0
        self.fields['activity_tuesday'].widget.attrs['value'] = 0
        self.fields['activity_wednesday'].widget.attrs['value'] = 0
        self.fields['activity_thursday'].widget.attrs['value'] = 0
        self.fields['activity_friday'].widget.attrs['value'] = 0
        self.fields['activity_saturday'].widget.attrs['value'] = 0
        self.fields['activity_sunday'].widget.attrs['value'] = 0
        self.fields['activity_total'].widget.attrs['value'] = 0
        self.fields['atId'].widget.attrs['value'] = 0


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ('name',)


# Form class to maintain timesheet records
def TimesheetFormset(currentUser, enddate):
    class TimeSheetEntryForm(forms.Form):
        project = forms.ModelChoiceField(
            queryset=None,
            label="Project",
            required=True,
        )
        location = forms.ModelChoiceField(
            queryset=None,
            required=True
        )

        chapter = forms.ModelChoiceField(widget=forms.Select(), queryset=Chapter.objects.none(),label="Chapter",)
        projectType = forms.CharField(label="pt",
                                      widget=forms.HiddenInput())
        task = forms.ModelChoiceField(widget=forms.Select(), queryset=Task.objects.none(), label="Task",)
        monday = forms.CharField(label="Mon", required=False)
        mondayH = forms.DecimalField(label="Hours",
                                     max_digits=12,
                                     decimal_places=2,
                                     widget=forms.HiddenInput()
                                     , required=False)
        mondayQ = forms.DecimalField(label="Questions",
                                     max_digits=12,
                                     decimal_places=2,
                                     widget=forms.HiddenInput()
                                     , required=False)
        tuesday = forms.CharField(label="Tue", required=False)
        tuesdayH = forms.DecimalField(label="Hours",
                                      max_digits=12,
                                      decimal_places=2,
                                      widget=forms.HiddenInput()
                                      , required=False)
        tuesdayQ = forms.DecimalField(label="Questions",
                                      max_digits=12,
                                      decimal_places=2,
                                      widget=forms.HiddenInput()
                                      , required=False)
        wednesday = forms.CharField(label="Wed", required=False)
        wednesdayH = forms.DecimalField(label="Hours",
                                        max_digits=12,
                                        decimal_places=2,
                                        widget=forms.HiddenInput()
                                        , required=False)
        wednesdayQ = forms.DecimalField(label="Questions",
                                        max_digits=12,
                                        decimal_places=2,
                                        widget=forms.HiddenInput()
                                        , required=False)
        thursday = forms.CharField(label="Thu", required=False)
        thursdayH = forms.DecimalField(label="Hours",
                                       max_digits=12,
                                       decimal_places=2,
                                       widget=forms.HiddenInput()
                                       , required=False)
        thursdayQ = forms.DecimalField(label="Questions",
                                       max_digits=12,
                                       decimal_places=2,
                                       widget=forms.HiddenInput()
                                       , required=False)
        friday = forms.CharField(label="Fri", required=False)
        fridayH = forms.DecimalField(label="Hours",
                                     max_digits=12,
                                     decimal_places=2,
                                     widget=forms.HiddenInput()
                                     , required=False)
        fridayQ = forms.DecimalField(label="Questions",
                                     max_digits=12,
                                     decimal_places=2,
                                     widget=forms.HiddenInput()
                                     , required=False)
        saturday = forms.CharField(label="Sat", required=False)
        saturdayH = forms.DecimalField(label="Hours",
                                       max_digits=12,
                                       decimal_places=2,
                                       widget=forms.HiddenInput()
                                       , required=False)
        saturdayQ = forms.DecimalField(label="Questions",
                                       max_digits=12,
                                       decimal_places=2,
                                       widget=forms.HiddenInput()
                                       , required=False)
        sunday = forms.CharField(label="Sun", required=False)
        sundayH = forms.DecimalField(label="Hours",
                                     max_digits=12,
                                     decimal_places=2,
                                     widget=forms.HiddenInput()
                                     , required=False)
        sundayQ = forms.DecimalField(label="Questions",
                                     max_digits=12,
                                     decimal_places=2,
                                     widget=forms.HiddenInput()
                                     , required=False)
        total = forms.CharField(label="Total", required=False)
        totalH = forms.DecimalField(label="Hours",
                                    max_digits=12,
                                    decimal_places=2,
                                    widget=forms.HiddenInput())
        totalQ = forms.DecimalField(label="Questions",
                                    max_digits=12,
                                    decimal_places=2,
                                    widget=forms.HiddenInput())

        tsId = forms.IntegerField(label="id",
                                  required=False,
                                  widget=forms.HiddenInput())
        approved = forms.BooleanField(label="approved",
                                      required=False)
        hold = forms.BooleanField(label="hold",
                                  required=False)

        def __init__(self, *args, **kwargs):
            super(TimeSheetEntryForm, self).__init__(*args, **kwargs)
            self.fields['project'].queryset = Project.objects.filter(
                # closed=False,
                endDate__gte=enddate,
                # endDate__gte=datetime.date.today(),
                id__in=ProjectTeamMember.objects.filter(
                    Q(member=currentUser.id) |
                    Q(project__projectManager=currentUser.id)
                ).values('project_id')
            ).order_by('name')

            project_id = self.fields['project'].initial\
                         or self.initial.get('project') \
                         or self.fields['project'].widget.value_from_datadict\
                             (self.data, self.files, self.add_prefix('project'))
            if project_id:
                project_obj = Project.objects.get(id=int(project_id))
                self.fields['chapter'].queryset = Chapter.objects.filter(book=project_obj.book)
                self.fields['task'].queryset = Task.objects.filter(projectType=project_obj.projectType, active=True)
            self.fields['location'].queryset = OfficeLocation.objects.filter(
                active=True)
            self.fields['project'].widget.attrs[
                'class'] = "form-control d-item \
                billable-select-project set-empty"
            self.fields['tsId'].widget.attrs['class'] = "set-zero"
            self.fields['location'].widget.attrs['class'] = \
                "form-control d-item set-zero"
            self.fields['chapter'].widget.attrs[
                'class'] = "form-control d-item b-chapter \
                remove-sel-options set-zero"
            self.fields['task'].widget.attrs[
                'class'
            ] = "form-control d-item b-task remove-sel-options set-zero"
            self.fields['mondayQ'].widget.attrs[
                'class'
            ] = "b-questions-hidden d-item set-zero"
            self.fields['mondayH'].widget.attrs[
                'class'
            ] = "b-hours-hidden d-item set-zero"
            self.fields['tuesdayQ'].widget.attrs[
                'class'
            ] = "b-questions-hidden d-item set-zero"
            self.fields['tuesdayH'].widget.attrs[
                'class'
            ] = "b-hours-hidden d-item set-zero"
            self.fields['wednesdayQ'].widget.attrs[
                'class'
            ] = "b-questions-hidden d-item set-zero"
            self.fields['wednesdayH'].widget.attrs[
                'class'
            ] = "b-hours-hidden d-item set-zero"
            self.fields['thursdayQ'].widget.attrs[
                'class'
            ] = "b-questions-hidden d-item set-zero"
            self.fields['thursdayH'].widget.attrs[
                'class'
            ] = "b-hours-hidden d-item set-zero"
            self.fields['fridayQ'].widget.attrs[
                'class'
            ] = "b-questions-hidden d-item set-zero"
            self.fields['fridayH'].widget.attrs[
                'class'
            ] = "b-hours-hidden d-item set-zero"
            self.fields['saturdayQ'].widget.attrs[
                'class'
            ] = "b-questions-hidden d-item set-zero"
            self.fields['saturdayH'].widget.attrs[
                'class'
            ] = "b-hours-hidden d-item set-zero"
            self.fields['sundayQ'].widget.attrs[
                'class'
            ] = "b-questions-hidden d-item set-zero"
            self.fields['sundayH'].widget.attrs[
                'class'
            ] = "b-hours-hidden d-item set-zero"
            self.fields['totalQ'].widget.attrs[
                'class'
            ] = "t-questions-hidden d-item set-zero"
            self.fields['totalH'].widget.attrs[
                'class'
            ] = "t-hours-hidden d-item set-zero"
            self.fields['mondayH'].widget.attrs['value'] = 0
            self.fields['mondayQ'].widget.attrs['value'] = 0.0
            self.fields['tuesdayH'].widget.attrs['value'] = 0
            self.fields['tuesdayQ'].widget.attrs['value'] = 0.0
            self.fields['wednesdayH'].widget.attrs['value'] = 0
            self.fields['wednesdayQ'].widget.attrs['value'] = 0.0
            self.fields['thursdayH'].widget.attrs['value'] = 0
            self.fields['thursdayQ'].widget.attrs['value'] = 0.0
            self.fields['fridayH'].widget.attrs['value'] = 0
            self.fields['fridayQ'].widget.attrs['value'] = 0.0
            self.fields['saturdayH'].widget.attrs['value'] = 0
            self.fields['saturdayQ'].widget.attrs['value'] = 0.0
            self.fields['sundayH'].widget.attrs['value'] = 0
            self.fields['sundayQ'].widget.attrs['value'] = 0.0
            self.fields['totalH'].widget.attrs['value'] = 0
            self.fields['totalQ'].widget.attrs['value'] = 0.0
            self.fields['tsId'].widget.attrs['value'] = 0
            self.fields['projectType'].widget.attrs['value'] = 'Q'

    return TimeSheetEntryForm


# Form Class to create project
class ProjectBasicInfoForm(forms.ModelForm):
    book = forms.ModelChoiceField(
        queryset=Book.objects.all(),
        label="Book/Title",
        widget=autocomplete.ModelSelect2(url='AutocompleteBook', attrs={
            # Set some placeholder
            'data-placeholder': 'Type Book/Title Name ...',
            # Only trigger autocompletion after 3 characters have been typed
            # 'data-minimum-input-length': 3,
        }, ),
        required=True, )
    projectManager = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Project Leader",
        widget=autocomplete.ModelSelect2(url='AutocompleteUser', attrs={
            # Set some placeholder
            'data-placeholder': 'Type Employee Name ...',
            # Only trigger autocompletion after 3 characters have been typed
            # 'data-minimum-input-length': 3,
        }, ),
        required=True, )

    class Meta:
        model = Project
        fields = (
            'projectType',
            'bu',
            'customer',
            'name',
            'customerContact',
            'book',
            'projectManager',
            'signed',
            'currentProject',
        )
        widgets = {
            'currentProject': forms.RadioSelect(
                choices=[(True, 'New Development'), (False, 'Revision')]
            ),
            'signed': forms.RadioSelect(
                choices=[(True, 'Yes'), (False, 'No')]
            ),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectBasicInfoForm, self).__init__(*args, **kwargs)
        self.fields['projectType'].widget.attrs['class'] = \
            "form-control"
        self.fields['projectType'].queryset = \
            projectType.objects.filter(active=True).order_by('description')
        self.fields['bu'].queryset = \
            BusinessUnit.objects.all().order_by('name')
        self.fields['customer'].queryset = \
            Customer.objects.filter(active=True).order_by('name')
        self.fields['projectManager'].widget.attrs['class'] = \
            "form-control"
        self.fields['bu'].widget.attrs['class'] = \
            "form-control"
        self.fields['customer'].widget.attrs['class'] = \
            "form-control"
        self.fields['name'].widget.attrs['class'] = \
            "form-control"
        self.fields['book'].widget.attrs['class'] = \
            "form-control"
        self.fields['book'].widget.attrs['id'] = \
            "id_Define_Project-book"
        self.fields['currentProject'].widget.attrs['class'] = \
            "form-control"
        self.fields['customerContact'].widget.attrs['class'] = \
            "form-control"
        self.fields['signed'].widget.attrs['class'] = \
            "form-control"


# Change Project Basic Form
class ChangeProjectForm(forms.ModelForm):
    class Meta:
        model = ProjectChangeInfo
        fields = ('project',)

        widgets = {
            'project': forms.RadioSelect()
        }

    def __init__(self, *args, **kwargs):
        super(ChangeProjectForm, self).__init__(*args, **kwargs)
        self.fields['project'].empty_label = None


class ChangeProjectBasicInfoForm(forms.ModelForm):
    id = forms.IntegerField(label="BasicInfoId", widget=forms.HiddenInput())

    class Meta:
        model = ProjectChangeInfo
        fields = (
            'reason', 'endDate', 'revisedEffort',
            'revisedTotal', 'salesForceNumber', 'po', 'closed', 'signed'
        )
        widgets = {
            'endDate': DateTimePicker(options=dateTimeOption),
        }

    def __init__(self, *args, **kwargs):
        super(ChangeProjectBasicInfoForm, self).__init__(*args, **kwargs)
        self.fields['id'].widget.attrs['value'] = 0
        self.fields['reason'].widget.attrs['class'] = "form-control"
        self.fields['endDate'].widget.attrs['class'] = "form-control"
        self.fields['revisedEffort'].widget.attrs['class'] = "form-control"
        self.fields['revisedTotal'].widget.attrs['class'] = "form-control"
        self.fields['closed'].widget.attrs['class'] = "form-control"
        self.fields['signed'].widget.attrs['class'] = "form-control"
        self.fields['salesForceNumber'].widget.attrs['class'] = "form-control"
        self.fields['salesForceNumber'].widget.attrs['min'] = "20100000"
        self.fields['salesForceNumber'].widget.attrs['max'] = "99999999"
        self.fields['po'].widget.attrs['class'] = "form-control"


class ChangeProjectTeamMemberForm(forms.ModelForm):
    id = forms.IntegerField(label="teamRecId", widget=forms.HiddenInput())
    member = forms.ModelChoiceField(
        queryset=User.objects.all(),
        # label="Project Leader",
        widget=autocomplete.ModelSelect2(url='AutocompleteUser', attrs={
            # Set some placeholder
            'data-placeholder': 'Type Employee Name ...',
            # Only trigger autocompletion after 3 characters have been typed
            # 'data-minimum-input-length': 3,
        }, ),
        required=True, )
    class Meta:
        model = ProjectTeamMember
        fields = (
            'member',
            'datapoint',
            'startDate',
            'endDate',
            'rate',
            'plannedEffort',
        )
        widgets = {
            'startDate': DateTimePicker(options=dateTimeOption),
            'endDate': DateTimePicker(options=dateTimeOption),
            'project': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ChangeProjectTeamMemberForm, self).__init__(*args, **kwargs)
        self.fields['id'].widget.attrs['value'] = 0
        self.fields['id'].widget.attrs['class'] = "set-zero"
        self.fields['member'].widget.attrs['class'] = "form-control min-200"
        self.fields['datapoint'].widget.attrs['class'] = "form-control min-200"
        self.fields['startDate'].widget.attrs[
            'class'] = "form-control min-100 pro-start-date"
        self.fields['endDate'].widget.attrs[
            'class'] = "form-control  min-100 pro-end-date"
        self.fields['rate'].widget.attrs[
            'class'] = "form-control w-100 pro-planned-effort-percent"
        self.fields['plannedEffort'].widget.attrs[
            'class'] = "form-control w-100 pro-planned-effort"


class CloseProjectMilestoneForm(forms.ModelForm):
    id = forms.IntegerField(label="msRecId", widget=forms.HiddenInput())

    class Meta:
        model = ProjectMilestone
        fields = (
            'milestoneDate', 'description',
            'amount', 'closed', 'financial'
        )
        widgets = {
            'project': forms.HiddenInput(),
            'milestoneDate': DateTimePicker(options=dateTimeOption),
        }

    def __init__(self, *args, **kwargs):
        super(CloseProjectMilestoneForm, self).__init__(*args, **kwargs)
        self.fields['id'].widget.attrs['value'] = 0
        self.fields['milestoneDate'].widget.attrs['class'] = \
            "date-picker d-item form-control"
        self.fields['description'].widget.attrs['class'] = \
            "d-item input-item form-control"
        self.fields['financial'].widget.attrs['class'] = \
            "d-item input-item form-control"
        self.fields['amount'].widget.attrs['class'] = \
            "milestone-item-amount d-item input-item form-control"
        self.fields['closed'].widget.attrs['class'] = "form-control"


# Project Flag Form
class ProjectFlagForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            'startDate',
            'endDate',
            'plannedEffort',
            'totalValue',
            'po',
            'salesForceNumber'
        )
        widgets = {
            'startDate': DateTimePicker(options=dateTimeOption),
            'endDate': DateTimePicker(options=dateTimeOption),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectFlagForm, self).__init__(*args, **kwargs)
        self.fields['po'].widget.attrs['class'] = \
            "form-control"
        self.fields['salesForceNumber'].widget.attrs['class'] = \
            "form-control"
        self.fields['salesForceNumber'].widget.attrs['min'] = \
            "20100000"
        self.fields['salesForceNumber'].widget.attrs['max'] = \
            "99999999"
        self.fields['plannedEffort'].widget.attrs['class'] = \
            "planned-effort-input form-control"
        self.fields['totalValue'].widget.attrs['class'] = \
            "total-value-input form-control"
        self.fields['startDate'].widget.attrs['class'] = \
            "start-date-input form-control"
        self.fields['endDate'].widget.attrs['class'] = \
            "end-date-input form-control"


# Form Class to create milestones for project
class changeProjectLeaderForm(forms.ModelForm):
    projectManager = forms.ModelChoiceField(
        queryset=User.objects.all(),
        # label="Project Leader",
        widget=autocomplete.ModelSelect2(url='AutocompleteUser', attrs={
            # Set some placeholder
            'data-placeholder': 'Type Employee Name ...',
            # Only trigger autocompletion after 3 characters have been typed
            # 'data-minimum-input-length': 3,
        }, ),
        required=True, )

    class Meta:
        model = Project
        fields = ('projectManager',)

    def __init__(self, *args, **kwargs):
        super(changeProjectLeaderForm, self).__init__(*args, **kwargs)
        self.fields['projectManager'].widget.attrs['class'] = "form-control"


class MyRemainderForm(forms.ModelForm):
    class Meta:
        model = Remainder
        fields = ('name', 'startDate', 'endDate')

        widgets = {
            'startDate': DateTimePicker(options=dateTimeOption),
            'endDate': DateTimePicker(options=dateTimeOption),
        }

    def __init__(self, *args, **kwargs):
        super(MyRemainderForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = "form-control"
        self.fields['startDate'].widget.attrs['class'] = "form-control"
        self.fields['endDate'].widget.attrs['class'] = "form-control"


# Form Class to create front-End Login
class LoginForm(forms.Form):
    userid = forms.CharField(max_length=30)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['userid'].widget.attrs['autofocus'] = "autofocus"


# Reports
class TeamMemberPerfomanceReportForm(forms.ModelForm):
    startDate = forms.DateField(
        label="From",
        widget=DateTimePicker(options=dateTimeOption),
        initial=timezone.now
    )
    endDate = forms.DateField(
        label="To",
        widget=DateTimePicker(options=dateTimeOption),
        initial=timezone.now
    )
    # project = forms.ModelChoiceField(
    #     queryset=None,
    #     label="Project",
    #     required=False, help_text="Leave blank for all",
    # )
    project = forms.ModelChoiceField(
        queryset=Project.objects.all().order_by('name'),
        # label="Book/Title",
        widget=autocomplete.ModelSelect2(url='AutocompleteProjects', attrs={
            # Set some placeholder
            'data-placeholder': 'Enter a Project Name /Project Id ...',
            # Only trigger autocompletion after 3 characters have been typed
            # 'data-minimum-input-length': 3,
        }, ),
        required=True, )

    class Meta:
        model = ProjectTeamMember
        fields = (
            'member',
        )

    def __init__(self, *args, **kwargs):
        super(TeamMemberPerfomanceReportForm, self).__init__(*args, **kwargs)
        self.fields['member'].widget.attrs['class'] = "form-control"
        self.fields['member'].required = True
        self.fields['startDate'].widget.attrs['class'] = "form-control"
        self.fields['endDate'].widget.attrs['class'] = "form-control"

        # self.fields['project'].queryset = Project.objects.all().order_by('name')
        # self.fields['project'].widget = autocomplete_light.ChoiceWidget('ProjectAutocompleteProjects')
        self.fields['project'].widget.attrs['class'] = "form-control"
        # self.fields['project'].widget.attrs['placeholder'] = 'Enter a Project Name /Project Id'


class ProjectPerfomanceReportForm(forms.Form):
    project = forms.ModelChoiceField(
        queryset=None,
        label="Project",
        widget=autocomplete.ModelSelect2(url='AutocompleteProjects', attrs={
            # Set some placeholder
            'data-placeholder': 'Enter a Project Name /Project Id ...',
            # Only trigger autocompletion after 3 characters have been typed
            # 'data-minimum-input-length': 3,
        }, ),
        required=True, )

    def __init__(self, *args, **kwargs):
        currentUser = kwargs.pop('user')
        super(ProjectPerfomanceReportForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.filter(
            id__in=helper.get_my_project_list(currentUser)).order_by('name')
        # self.fields['project'].widget = autocomplete_light.ChoiceWidget('ProjectAutocompleteProjects')
        self.fields['project'].widget.attrs['class'] = "form-control"
        # self.fields['project'].widget.attrs['placeholder'] = 'Enter a Project Name /Project Id'


class UtilizationReportForm(forms.Form):
    bu = forms.ChoiceField(
        label="Business Unit",
        required=True,
    )
    month = forms.ChoiceField(choices=MONTHS)
    year = forms.ChoiceField(choices=YEARS)

    def __init__(self, *args, **kwargs):
        currentUser = kwargs.pop('user')
        super(UtilizationReportForm, self).__init__(*args, **kwargs)
        # import ipdb;ipdb.set_trace()
        if currentUser.is_superuser:
            bu = list(BusinessUnit.objects.all())
            opt = [(0, 'All')] + [(rec.id, rec.name) for rec in bu]
            self.fields['bu'].choices = opt
        else:
            bu = list(
                BusinessUnit.objects.filter(
                    id__in=Project.objects.filter(
                        id__in=helper.get_my_project_list(currentUser)).values('bu__id')
                ).order_by('name'))
            self.fields['bu'].choices = [(rec.id, rec.name) for rec in bu]
        self.fields['bu'].widget.attrs['class'] = "form-control"
        self.fields['year'].widget.attrs['class'] = "form-control"
        self.fields['month'].widget.attrs['class'] = "form-control"


class BTGReportForm(forms.Form):
    month = forms.ChoiceField(choices=MONTHS)
    year = forms.ChoiceField(choices=YEARS)

    def __init__(self, *args, **kwargs):
        super(BTGReportForm, self).__init__(*args, **kwargs)
        self.fields['month'].widget.attrs['class'] = "form-control"
        self.fields['year'].widget.attrs['class'] = "form-control"


class InvoiceForm(forms.ModelForm):
    month = forms.ChoiceField(choices=MONTHS)
    year = forms.ChoiceField(choices=YEARS)

    class Meta:
        model = BTGReport
        fields = ('project', 'currMonthIN')

    def __init__(self, *args, **kwargs):
        currentUser = kwargs.pop('user')
        super(InvoiceForm, self).__init__(*args, **kwargs)
        pr = Project.objects.filter(
            id__in=ProjectManager.objects.filter(
                user=currentUser
            ).values('project')
        )
        self.fields['project'].queryset = pr
        self.fields['project'].widget.attrs['class'] = "form-control"
        self.fields['month'].widget.attrs['class'] = "form-control"
        self.fields['year'].widget.attrs['class'] = "form-control"
        self.fields['currMonthIN'].widget.attrs['class'] = "form-control"


class BTGForm(forms.ModelForm):
    month = forms.ChoiceField(choices=MONTHS)
    year = forms.ChoiceField(choices=YEARS)

    class Meta:
        model = BTGReport
        fields = ('project', 'btg')

    def __init__(self, *args, **kwargs):
        currentUser = kwargs.pop('user')
        super(BTGForm, self).__init__(*args, **kwargs)
        pr = Project.objects.filter(
            id__in=ProjectManager.objects.filter(
                user=currentUser
            ).values('project')
        )
        self.fields['project'].queryset = pr
        self.fields['project'].widget.attrs['class'] = "form-control"
        self.fields['month'].widget.attrs['class'] = "form-control"
        self.fields['year'].widget.attrs['class'] = "form-control"
        self.fields['btg'].widget.attrs['class'] = "form-control"
