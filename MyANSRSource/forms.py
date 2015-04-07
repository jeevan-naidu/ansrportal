import autocomplete_light
autocomplete_light.autodiscover()
from django.db.models import Q
from django import forms
from MyANSRSource.models import Project, ProjectTeamMember, \
    ProjectMilestone, Chapter, ProjectChangeInfo, Activity, Task
from bootstrap3_datetime.widgets import DateTimePicker
from CompanyMaster.models import OfficeLocation

dateTimeOption = {"format": "YYYY-MM-DD", "pickTime": False}


class ActivityForm(forms.Form):
    activity = forms.ModelChoiceField(
        queryset=Activity.objects.all(),
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
                                        max_value=24.0,
                                        decimal_places=2,
                                        )
    activity_feedback = forms.CharField(
        max_length="50", label="Feedback", required=False
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
        self.fields['activity_feedback'].widget.attrs['readonly'] = 'True'
        self.fields['activity_total'].widget.attrs['readonly'] = 'True'
        self.fields['activity'].widget.attrs['class'] = "form-control"
        self.fields['activity_monday'].widget.attrs['class'] = "form-control \
        days input-field Mon-t"
        self.fields['activity_tuesday'].widget.attrs['class'] = "form-control \
        days input-field Tue-t"
        self.fields['activity_wednesday'].widget.attrs['class'] = "form-control \
        days input-field Wed-t"
        self.fields['activity_thursday'].widget.attrs['class'] = "form-control \
        days input-field Thu-t"
        self.fields['activity_friday'].widget.attrs['class'] = "form-control \
        days input-field Fri-t"
        self.fields['activity_saturday'].widget.attrs['class'] = "form-control \
        days input-field Sat-t"
        self.fields['activity_sunday'].widget.attrs['class'] = "form-control \
        days input-field Sun-t"
        self.fields['activity_total'].widget.attrs['class'] = "form-control \
        total input-field r-total"
        self.fields['activity_feedback'].widget.attrs['class'] = "form-control"
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
def TimesheetFormset(currentUser):
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
        chapter = forms.ModelChoiceField(
            queryset=Chapter.objects.all(),
            required=False,
        )
        projectType = forms.CharField(label="pt",
                                      widget=forms.HiddenInput())
        task = forms.ModelChoiceField(
            queryset=Task.objects.all(),
            label="Task",
            required=True,
        )
        monday = forms.CharField(label="Mon", required=False)
        mondayH = forms.DecimalField(label="Hours",
                                     max_digits=12,
                                     decimal_places=2,
                                     widget=forms.HiddenInput())
        mondayQ = forms.DecimalField(label="Questions",
                                     max_digits=12,
                                     decimal_places=2,
                                     widget=forms.HiddenInput())
        tuesday = forms.CharField(label="Tue", required=False)
        tuesdayH = forms.DecimalField(label="Hours",
                                      max_digits=12,
                                      decimal_places=2,
                                      widget=forms.HiddenInput())
        tuesdayQ = forms.DecimalField(label="Questions",
                                      max_digits=12,
                                      decimal_places=2,
                                      widget=forms.HiddenInput())
        wednesday = forms.CharField(label="Wed", required=False)
        wednesdayH = forms.DecimalField(label="Hours",
                                        max_digits=12,
                                        decimal_places=2,
                                        widget=forms.HiddenInput())
        wednesdayQ = forms.DecimalField(label="Questions",
                                        max_digits=12,
                                        decimal_places=2,
                                        widget=forms.HiddenInput())
        thursday = forms.CharField(label="Thu", required=False)
        thursdayH = forms.DecimalField(label="Hours",
                                       max_digits=12,
                                       decimal_places=2,
                                       widget=forms.HiddenInput())
        thursdayQ = forms.DecimalField(label="Questions",
                                       max_digits=12,
                                       decimal_places=2,
                                       widget=forms.HiddenInput())
        friday = forms.CharField(label="Fri", required=False)
        fridayH = forms.DecimalField(label="Hours",
                                     max_digits=12,
                                     decimal_places=2,
                                     widget=forms.HiddenInput())
        fridayQ = forms.DecimalField(label="Questions",
                                     max_digits=12,
                                     decimal_places=2,
                                     widget=forms.HiddenInput())
        saturday = forms.CharField(label="Sat", required=False)
        saturdayH = forms.DecimalField(label="Hours",
                                       max_digits=12,
                                       decimal_places=2,
                                       widget=forms.HiddenInput())
        saturdayQ = forms.DecimalField(label="Questions",
                                       max_digits=12,
                                       decimal_places=2,
                                       widget=forms.HiddenInput())
        sunday = forms.CharField(label="Sun", required=False)
        sundayH = forms.DecimalField(label="Hours",
                                     max_digits=12,
                                     decimal_places=2,
                                     widget=forms.HiddenInput())
        sundayQ = forms.DecimalField(label="Questions",
                                     max_digits=12,
                                     decimal_places=2,
                                     widget=forms.HiddenInput())
        total = forms.CharField(label="Total", required=False)
        totalH = forms.DecimalField(label="Hours",
                                    max_digits=12,
                                    decimal_places=2,
                                    widget=forms.HiddenInput())
        totalQ = forms.DecimalField(label="Questions",
                                    max_digits=12,
                                    decimal_places=2,
                                    widget=forms.HiddenInput())
        feedback = forms.CharField(
            max_length="50", label="Feedback", required=False
        )
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
                closed=False,
                id__in=ProjectTeamMember.objects.filter(
                    Q(member=currentUser.id) |
                    Q(project__projectManager=currentUser.id)
                ).values('project_id')
            )
            self.fields['location'].queryset = OfficeLocation.objects.all()
            if hasattr(currentUser, 'employee'):
                self.initial['location'] = currentUser.employee.location
            self.fields['project'].widget.attrs[
                'class'] = "form-control d-item billable-select-project"
            self.fields['location'].widget.attrs['class'] = \
                "form-control d-item"
            self.fields['chapter'].widget.attrs[
                'class'] = "form-control d-item b-chapter remove-sel-options"
            self.fields['task'].widget.attrs[
                'class'
            ] = "form-control d-item b-task remove-sel-options"
            self.fields['mondayQ'].widget.attrs[
                'class'
            ] = "b-questions-hidden d-item"
            self.fields['mondayH'].widget.attrs[
                'class'
            ] = "b-hours-hidden d-item"
            self.fields['tuesdayQ'].widget.attrs[
                'class'
            ] = "b-questions-hidden d-item"
            self.fields['tuesdayH'].widget.attrs[
                'class'
            ] = "b-hours-hidden d-item"
            self.fields['wednesdayQ'].widget.attrs[
                'class'
            ] = "b-questions-hidden d-item"
            self.fields['wednesdayH'].widget.attrs[
                'class'
            ] = "b-hours-hidden d-item"
            self.fields['thursdayQ'].widget.attrs[
                'class'
            ] = "b-questions-hidden d-item"
            self.fields['thursdayH'].widget.attrs[
                'class'
            ] = "b-hours-hidden d-item"
            self.fields['fridayQ'].widget.attrs[
                'class'
            ] = "b-questions-hidden d-item"
            self.fields['fridayH'].widget.attrs[
                'class'
            ] = "b-hours-hidden d-item"
            self.fields['saturdayQ'].widget.attrs[
                'class'
            ] = "b-questions-hidden d-item"
            self.fields['saturdayH'].widget.attrs[
                'class'
            ] = "b-hours-hidden d-item"
            self.fields['sundayQ'].widget.attrs[
                'class'
            ] = "b-questions-hidden d-item"
            self.fields['sundayH'].widget.attrs[
                'class'
            ] = "b-hours-hidden d-item"
            self.fields['totalQ'].widget.attrs[
                'class'
            ] = "t-questions-hidden d-item"
            self.fields['totalH'].widget.attrs[
                'class'
            ] = "t-hours-hidden d-item"
            self.fields['feedback'].widget.attrs[
                'class'
            ] = "form-control d-item"
            self.fields['feedback'].widget.attrs['readonly'] = 'True'
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
class ProjectBasicInfoForm(autocomplete_light.ModelForm):

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
            'internal',
            'currentProject',
        )
        widgets = {
            'currentProject': forms.RadioSelect(
                choices=[(True, 'New Development'), (False, 'Revision')]
            ),
            'signed': forms.RadioSelect(
                choices=[(True, 'Yes'), (False, 'No')]
            ),
            'internal': forms.RadioSelect(
                choices=[(True, 'Yes'), (False, 'No')]
            )
        }

    def __init__(self, *args, **kwargs):
        super(ProjectBasicInfoForm, self).__init__(*args, **kwargs)
        self.fields['projectType'].widget.attrs['class'] = \
            "form-control"
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
        self.fields['internal'].widget.attrs['class'] = \
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
        self.fields['po'].widget.attrs['class'] = "form-control"


class ChangeProjectTeamMemberForm(autocomplete_light.ModelForm):

    id = forms.IntegerField(label="teamRecId", widget=forms.HiddenInput())

    class Meta:
        model = ProjectTeamMember
        fields = (
            'member',
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
            'maxProductivityUnits',
            'startDate',
            'endDate',
            'plannedEffort',
            'contingencyEffort',
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
        self.fields['maxProductivityUnits'].widget.attrs['class'] = \
            "form-control"
        self.fields['po'].widget.attrs['class'] = \
            "form-control"
        self.fields['salesForceNumber'].widget.attrs['class'] = \
            "form-control"
        self.fields['plannedEffort'].widget.attrs['class'] = \
            "planned-effort-input form-control"
        self.fields['contingencyEffort'].widget.attrs['class'] = \
            "contigency-effort-input form-control"
        self.fields['totalValue'].widget.attrs['class'] = \
            "total-value-input form-control"
        self.fields['startDate'].widget.attrs['class'] = \
            "start-date-input form-control"
        self.fields['endDate'].widget.attrs['class'] = \
            "end-date-input form-control"


# Form Class to create milestones for project
class changeProjectLeaderForm(autocomplete_light.ModelForm):

    class Meta:
        model = Project
        fields = ('projectManager',)

    def __init__(self, *args, **kwargs):
        super(changeProjectLeaderForm, self).__init__(*args, **kwargs)
        self.fields['projectManager'].widget.attrs['class'] = "form-control"


# Form Class to create front-End Login
class LoginForm(forms.Form):
    userid = forms.CharField(max_length=30)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['userid'].widget.attrs['autofocus'] = "autofocus"
