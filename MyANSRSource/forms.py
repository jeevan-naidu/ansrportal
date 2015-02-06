import autocomplete_light
autocomplete_light.autodiscover()
from django.db.models import Q
from django import forms
from MyANSRSource.models import Project, ProjectTeamMember, \
    ProjectMilestone, Chapter, ProjectChangeInfo
from bootstrap3_datetime.widgets import DateTimePicker
from smart_selects.form_fields import ChainedModelChoiceField
import CompanyMaster

dateTimeOption = {"format": "YYYY-MM-DD", "pickTime": False}

TASK = (
    ('D', 'Develop'),
    ('E', 'EA'),
    ('C', 'CE'),
    ('Q', 'QA'),
    ('I', 'Idle'),
    ('W', 'Rework'),
)

NONBILLABLE = (
    ('S', 'Self Development'),
    ('R', 'Leave'),
    ('C', 'Training'),
    ('Q', 'Others'),
)


class ActivityForm(forms.Form):
    activity = forms.ChoiceField(choices=NONBILLABLE, label="Activity")
    activity_monday = forms.IntegerField(
        label="Mon",
        min_value=0,
        max_value=24
    )
    activity_tuesday = forms.IntegerField(
        label="Tue",
        min_value=0,
        max_value=24
    )
    activity_wednesday = forms.IntegerField(
        label="Wed",
        min_value=0,
        max_value=24
    )
    activity_thursday = forms.IntegerField(
        label="Thu",
        min_value=0,
        max_value=24
    )
    activity_friday = forms.IntegerField(
        label="Fri",
        min_value=0,
        max_value=24
    )
    activity_saturday = forms.IntegerField(
        label="Sat",
        min_value=0,
        max_value=24
    )
    activity_sunday = forms.IntegerField(
        label="Sun",
        min_value=0,
        max_value=24
    )
    activity_total = forms.IntegerField(
        label="Total",
        min_value=0,
        max_value=144,
        required=False
    )
    activity_feedback = forms.CharField(
        max_length="50", label="Feedback", required=False
    )
    atId = forms.IntegerField(label="id",
                              required=False,
                              widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)
        self.fields['activity_feedback'].widget.attrs['readonly'] = 'True'
        self.fields['activity_total'].widget.attrs['readonly'] = 'True'
        self.fields['activity'].widget.attrs['class'] = "form-control"
        self.fields['activity_monday'].widget.attrs['class'] = "form-control \
        days input-field"
        self.fields['activity_tuesday'].widget.attrs['class'] = "form-control \
        days input-field"
        self.fields['activity_wednesday'].widget.attrs['class'] = "form-control \
        days input-field"
        self.fields['activity_thursday'].widget.attrs['class'] = "form-control \
        days input-field"
        self.fields['activity_friday'].widget.attrs['class'] = "form-control \
        days input-field"
        self.fields['activity_saturday'].widget.attrs['class'] = "form-control \
        days input-field"
        self.fields['activity_sunday'].widget.attrs['class'] = "form-control \
        days input-field"
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
            queryset=CompanyMaster.models.OfficeLocation.objects.all(),
            label="Location",
            required=True
        )
        chapter = ChainedModelChoiceField(
            'MyANSRSource',
            'Chapter',
            chain_field='project',
            model_field='project',
            show_all=False,
            auto_choose=True
        )
        projectType = forms.CharField(label="pt",
                                      widget=forms.HiddenInput())
        task = forms.ChoiceField(choices=TASK, label='Task')
        monday = forms.CharField(label="Mon", required=False)
        mondayH = forms.IntegerField(label="Hours",
                                     widget=forms.HiddenInput())
        mondayQ = forms.IntegerField(label="Questions",
                                     widget=forms.HiddenInput())
        tuesday = forms.CharField(label="Tue", required=False)
        tuesdayH = forms.IntegerField(label="Hours",
                                      widget=forms.HiddenInput())
        tuesdayQ = forms.IntegerField(label="Questions",
                                      widget=forms.HiddenInput())
        wednesday = forms.CharField(label="Wed", required=False)
        wednesdayH = forms.IntegerField(label="Hours",
                                        widget=forms.HiddenInput())
        wednesdayQ = forms.IntegerField(label="Questions",
                                        widget=forms.HiddenInput())
        thursday = forms.CharField(label="Thu", required=False)
        thursdayH = forms.IntegerField(label="Hours",
                                       widget=forms.HiddenInput())
        thursdayQ = forms.IntegerField(label="Questions",
                                       widget=forms.HiddenInput())
        friday = forms.CharField(label="Fri", required=False)
        fridayH = forms.IntegerField(label="Hours",
                                     widget=forms.HiddenInput())
        fridayQ = forms.IntegerField(label="Questions",
                                     widget=forms.HiddenInput())
        saturday = forms.CharField(label="Sat", required=False)
        saturdayH = forms.IntegerField(label="Hours",
                                       widget=forms.HiddenInput())
        saturdayQ = forms.IntegerField(label="Questions",
                                       widget=forms.HiddenInput())
        sunday = forms.CharField(label="Sun", required=False)
        sundayH = forms.IntegerField(label="Hours",
                                     widget=forms.HiddenInput())
        sundayQ = forms.IntegerField(label="Questions",
                                     widget=forms.HiddenInput())
        total = forms.CharField(label="Total", required=False)
        totalH = forms.IntegerField(label="Hours",
                                    widget=forms.HiddenInput())
        totalQ = forms.IntegerField(label="Questions",
                                    widget=forms.HiddenInput())
        feedback = forms.CharField(
            max_length="50", label="Feedback", required=False
        )
        tsId = forms.IntegerField(label="id",
                                  required=False,
                                  widget=forms.HiddenInput())

        def __init__(self, *args, **kwargs):
            super(TimeSheetEntryForm, self).__init__(*args, **kwargs)
            self.fields['project'].queryset = Project.objects.filter(
                id__in=ProjectTeamMember.objects.filter(
                    Q(member=currentUser.id) |
                    Q(project__projectManager=currentUser.id)
                ).values('project_id')
            )
            if currentUser.has_perm('MyANSRSource.manage_project'):
                self.fields['chapter'] = ChainedModelChoiceField(
                    'MyANSRSource',
                    'Chapter',
                    chain_field='project',
                    model_field='project',
                    show_all=False,
                    auto_choose=False,
                    required=False
                )
            self.fields['project'].widget.attrs[
                'class'] = "form-control d-item billable-select-project"
            self.fields['location'].widget.attrs['class'] = \
                "form-control d-item"
            self.fields['chapter'].widget.attrs[
                'class'] = "form-control d-item"
            self.fields['task'].widget.attrs[
                'class'
            ] = "form-control d-item b-task"
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
            self.fields['mondayQ'].widget.attrs['value'] = 0
            self.fields['tuesdayH'].widget.attrs['value'] = 0
            self.fields['tuesdayQ'].widget.attrs['value'] = 0
            self.fields['wednesdayH'].widget.attrs['value'] = 0
            self.fields['wednesdayQ'].widget.attrs['value'] = 0
            self.fields['thursdayH'].widget.attrs['value'] = 0
            self.fields['thursdayQ'].widget.attrs['value'] = 0
            self.fields['fridayH'].widget.attrs['value'] = 0
            self.fields['fridayQ'].widget.attrs['value'] = 0
            self.fields['saturdayH'].widget.attrs['value'] = 0
            self.fields['saturdayQ'].widget.attrs['value'] = 0
            self.fields['sundayH'].widget.attrs['value'] = 0
            self.fields['sundayQ'].widget.attrs['value'] = 0
            self.fields['totalH'].widget.attrs['value'] = 0
            self.fields['totalQ'].widget.attrs['value'] = 0
            self.fields['tsId'].widget.attrs['value'] = 0
            self.fields['projectType'].widget.attrs['value'] = 'Q'
    return TimeSheetEntryForm


# Form Class to create project
class ProjectBasicInfoForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = (
            'projectType',
            'bu',
            'customer',
            'name',
            'startDate',
            'endDate',
            'book',
            'chapters',
            'plannedEffort',
            'contingencyEffort',
            'totalValue'
        )
        widgets = {
            'startDate': DateTimePicker(options=dateTimeOption),
            'endDate': DateTimePicker(options=dateTimeOption),
            'projectManager': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectBasicInfoForm, self).__init__(*args, **kwargs)
        self.fields['projectType'].widget.attrs['class'] = \
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
        self.fields['chapters'].widget.attrs['class'] = \
            "form-control"
        self.fields['chapters'].widget.attrs['id'] = \
            "id_Define_Project-chapters"
        self.fields['startDate'].widget.attrs['class'] = \
            "start-date-input form-control"
        self.fields['endDate'].widget.attrs['class'] = \
            "end-date-input form-control"
        self.fields['plannedEffort'].widget.attrs['class'] = \
            "planned-effort-input form-control"
        self.fields['contingencyEffort'].widget.attrs['class'] = \
            "contigency-effort-input form-control"
        self.fields['totalValue'].widget.attrs['class'] = \
            "total-value-input form-control"


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
            'revisedTotal', 'closed', 'signed'
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


class ChangeProjectTeamMemberForm(autocomplete_light.ModelForm):

    id = forms.IntegerField(label="teamRecId", widget=forms.HiddenInput())

    class Meta:
        model = ProjectTeamMember
        fields = (
            'member',
            'role',
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
        self.fields['id'].widget.attrs['class'] = 'set-zero'
        self.fields['member'].widget.attrs['class'] = "form-control min-200"
        self.fields['role'].widget.attrs[
            'class'] = "form-control min-180 max-200 set-empty"
        self.fields['startDate'].widget.attrs[
            'class'] = "form-control min-100 pro-start-date"
        self.fields['endDate'].widget.attrs[
            'class'] = "form-control  min-100 pro-end-date"
        self.fields['rate'].widget.attrs[
            'class'] = "form-control w-100 pro-planned-effort-percent"
        self.fields['plannedEffort'].widget.attrs[
            'class'] = "form-control w-100 pro-planned-effort"


class ChangeProjectMilestoneForm(forms.ModelForm):

    id = forms.IntegerField(label="msRecId", widget=forms.HiddenInput())

    class Meta:
        model = ProjectMilestone
        fields = (
            'milestoneDate', 'description',
            'amount'
        )
        widgets = {
            'milestoneDate': DateTimePicker(options=dateTimeOption),
            'project': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ChangeProjectMilestoneForm, self).__init__(*args, **kwargs)
        self.fields['id'].widget.attrs['value'] = 0
        self.fields['milestoneDate'].widget.attrs[
            'class'] = "form-control min-100"
        self.fields['description'].widget.attrs[
            'class'] = "form-control min-200"
        self.fields['amount'].widget.attrs[
            'class'] = "form-control w-100 milestone-item-amount"


class CloseProjectMilestoneForm(forms.ModelForm):

    id = forms.IntegerField(label="msRecId", widget=forms.HiddenInput())

    class Meta:
        model = ProjectMilestone
        fields = (
            'milestoneDate', 'description',
            'amount', 'reason', 'closed'
        )
        widgets = {
            'project': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(CloseProjectMilestoneForm, self).__init__(*args, **kwargs)
        self.fields['id'].widget.attrs['value'] = 0
        self.fields['milestoneDate'].widget.attrs['class'] = "form-control"
        self.fields['milestoneDate'].widget.attrs['readonly'] = 'True'
        self.fields['description'].widget.attrs['class'] = "form-control"
        self.fields['description'].widget.attrs['readonly'] = 'True'
        self.fields['amount'].widget.attrs['class'] = "form-control"
        self.fields['reason'].widget.attrs['class'] = "form-control"
        self.fields['closed'].widget.attrs['class'] = "form-control"


# Form Class to create team for project
class ProjectTeamForm(autocomplete_light.ModelForm):

    class Meta:
        model = ProjectTeamMember
        fields = (
            'member',
            'role',
            'startDate',
            'endDate',
            'rate',
            'plannedEffort',
        )
        widgets = {
            'startDate': DateTimePicker(options=dateTimeOption),
            'endDate': DateTimePicker(options=dateTimeOption),
            'project': forms.HiddenInput(), }

    def __init__(self, *args, **kwargs):
        super(ProjectTeamForm, self).__init__(*args, **kwargs)
        self.fields['member'].widget.attrs['class'] = "form-control min-200"
        self.fields['startDate'].widget.attrs['class'] = \
            "form-control pro-start-date min-100"
        self.fields['endDate'].widget.attrs['class'] = \
            "form-control pro-end-date min-100"
        self.fields['role'].widget.attrs['class'] = "form-control min-180 \
            max-200"
        self.fields['plannedEffort'].widget.attrs['class'] = \
            "w-100 form-control pro-planned-effort"
        self.fields['rate'].widget.attrs['class'] = \
            "w-100 form-control pro-planned-effort-percent"


# Project Flag Form
class ProjectFlagForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = (
            'currentProject',
            'signed',
            'internal', )
        widgets = {
            'currentProject': forms.RadioSelect(
                choices=[(True, 'New Development'), (False, 'Enhancement')]
            ),
            'signed': forms.RadioSelect(
                choices=[(True, 'Yes'), (False, 'No')]
            ),
            'internal': forms.RadioSelect(
                choices=[(True, 'Yes'), (False, 'No')]
            )
        }


# Form Class to create milestones for project
class ProjectMilestoneForm(forms.ModelForm):

    class Meta:
        model = ProjectMilestone
        fields = (
            'milestoneDate',
            'description',
            'amount'
        )
        widgets = {
            'milestoneDate': DateTimePicker(options=dateTimeOption),
            'project': forms.HiddenInput(), }

    def __init__(self, *args, **kwargs):
        super(ProjectMilestoneForm, self).__init__(*args, **kwargs)
        self.fields['milestoneDate'].widget.attrs['class'] = \
            "date-picker d-item form-control"
        self.fields['amount'].widget.attrs['class'] = \
            "milestone-item-amount d-item input-item form-control"
        self.fields['description'].widget.attrs['class'] = \
            "d-item input-item form-control"


# Form Class to create front-End Login
class LoginForm(forms.Form):
    userid = forms.CharField(max_length=30)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)
