
from django.db.models import Q
from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from MyANSRSource.models import Book, Project, ProjectTeamMember, \
    ProjectMilestone, Chapter, ProjectChangeInfo, Activity, Task, \
    projectType, ProjectManager, TimeSheetEntry, BTGReport, qualitysop, ProjectDetail, ProjectAsset, ProjectScope,\
    Milestone, ProjectSopTemplate,Role
from bootstrap3_datetime.widgets import DateTimePicker
from CompanyMaster.models import OfficeLocation, BusinessUnit, Customer, Practice, DataPoint
from employee.models import Remainder
from django.utils.safestring import mark_safe
import datetime
import calendar
import helper
from dal import autocomplete

PROJECT_CLOSE_FLAG = (('','................'),
                      ('Extending end date external (client side)', 'Extending end date external (client side)'),
                      ('Extending end date internal ', 'Extending end date internal '),
                      ('Extending end date for 0 value project ', 'Extending end date for 0 value project '),
                      ('Revising planned effort ', 'Revising planned effort '),
                      ('Revising planned effort for 0 value project ', 'Revising planned effort for 0 value project '),
                      ('Revising planned cost ', 'Revising planned cost '),
                      ('Revising planned cost for 0 value project ', 'Revising planned cost for 0 value project '),
                      ('Others', 'Others'),
                      ('Closing sample project', 'Closing sample project'),
                      ('Closing master project', 'Closing master project'),
                      ('Closing rework project', 'Closing rework project'),)

PROJECTFINTYPE = (
    ('', '-------'),
    ('FP', 'Fixed Price'),
    ('T&M', 'T&M')
)
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
                                         decimal_places=2
                                         )
    activity_tuesday = forms.DecimalField(label="Tue",
                                          max_digits=12,
                                          min_value=0.0,
                                          max_value=24.0,
                                          decimal_places=2
                                          )
    activity_wednesday = forms.DecimalField(label="Wed",
                                            max_digits=12,
                                            min_value=0.0,
                                            max_value=24.0,
                                            decimal_places=2
                                            )
    activity_thursday = forms.DecimalField(label="Thu",
                                           max_digits=12,
                                           min_value=0.0,
                                           max_value=24.0,
                                           decimal_places=2
                                           )
    activity_friday = forms.DecimalField(label="Fri",
                                         max_digits=12,
                                         min_value=0.0,
                                         max_value=24.0,
                                         decimal_places=2
                                         )
    activity_saturday = forms.DecimalField(label="Sat",
                                           max_digits=12,
                                           min_value=0.0,
                                           max_value=24.0,
                                           decimal_places=2
                                           )
    activity_sunday = forms.DecimalField(label="Sun",
                                         max_digits=12,
                                         min_value=0.0,
                                         max_value=24.0,
                                         decimal_places=2
                                         )
    activity_total = forms.DecimalField(label="Total",
                                        max_digits=12,
                                        min_value=0.0,
                                        decimal_places=2
                                        )

    atId = forms.IntegerField(label="id",
                              required=False,
                              widget=forms.HiddenInput())
    approved = forms.BooleanField(label="approved",
                                  required=False)
    hold = forms.BooleanField(label="hold",
                              required=False)
    # managerFeedback = forms.CharField(label="Feedback", required=False)
    remarks = forms.CharField(label="Remarks", required=False, widget=forms.Textarea(attrs={'cols': 100, 'rows': 5}))

    def __init__(self, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)
        self.fields['activity_total'].widget.attrs['readonly'] = 'True'
        self.fields['activity'].widget.attrs['class'] = "form-control non-billable-select-project"
        self.fields['activity_monday'].widget.attrs['class'] = "form-control \
        days input-field Mon-t 24hrcheck"
        self.fields['activity_tuesday'].widget.attrs['class'] = "form-control \
        days input-field Tue-t 24hrcheck"
        self.fields['activity_wednesday'].widget.attrs['class'] = "form-control \
        days input-field Wed-t 24hrcheck"
        self.fields['activity_thursday'].widget.attrs['class'] = "form-control \
        days input-field Thu-t 24hrcheck"
        self.fields['activity_friday'].widget.attrs['class'] = "form-control \
        days input-field Fri-t 24hrcheck"
        self.fields['activity_saturday'].widget.attrs['class'] = "form-control \
        days input-field Sat-t 24hrcheck"
        self.fields['activity_sunday'].widget.attrs['class'] = "form-control \
        days input-field Sun-t 24hrcheck"
        self.fields['activity_total'].widget.attrs['class'] = "form-control \
        total input-field r-total"
        self.fields['remarks'].widget.attrs[
            'class'
        ] = 'remarks set-empty'
        hold_value = self.fields['hold'].initial or self.initial.get('hold') or \
                     self.fields['hold'].widget.value_from_datadict(self.data, self.files, self.add_prefix('hold'))
        if hold_value:
            self.fields['activity_monday'].widget.attrs['readonly'] = True
            self.fields['activity_tuesday'].widget.attrs['readonly'] = True
            self.fields['activity_wednesday'].widget.attrs['readonly'] = True
            self.fields['activity_thursday'].widget.attrs['readonly'] = True
            self.fields['activity_friday'].widget.attrs['readonly'] = True
            self.fields['activity_saturday'].widget.attrs['readonly'] = True
            self.fields['activity_sunday'].widget.attrs['readonly'] = True
            self.fields['activity_total'].widget.attrs['readonly'] = True
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
def TimesheetFormset(currentUser,enddate):
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
        projectType = forms.CharField(label="pt", widget=forms.HiddenInput())
        task = forms.ModelChoiceField(widget=forms.Select(), queryset=Task.objects.none(), label="Task",)
        monday = forms.CharField(label="Mon", required=False)
        mondayH = forms.DecimalField(label="Hours",
                                     max_digits=12,
                                     min_value=0.0,
                                     max_value=24.0,
                                     decimal_places=2
                                     , required=False)

        tuesday = forms.CharField(label="Tue", required=False)
        tuesdayH = forms.DecimalField(label="Hours",
                                      max_digits=12,
                                      min_value=0.0,
                                      max_value=24.0,
                                      decimal_places=2
                                      , required=False)

        wednesday = forms.CharField(label="Wed", required=False)
        wednesdayH = forms.DecimalField(label="Hours",
                                        max_digits=12,
                                        min_value=0.0,
                                        max_value=24.0,
                                        decimal_places=2
                                        , required=False)

        thursday = forms.CharField(label="Thu", required=False)
        thursdayH = forms.DecimalField(label="Hours",
                                       max_digits=12,
                                       min_value=0.0,
                                       max_value=24.0,
                                       decimal_places=2
                                       , required=False)

        friday = forms.CharField(label="Fri", required=False)
        fridayH = forms.DecimalField(label="Hours",
                                     max_digits=12,
                                     min_value=0.0,
                                     max_value=24.0,
                                     decimal_places=2
                                     , required=False)

        saturday = forms.CharField(label="Sat", required=False)
        saturdayH = forms.DecimalField(label="Hours",
                                       max_digits=12,
                                       min_value=0.0,
                                       max_value=24.0,
                                       decimal_places=2
                                       , required=False)

        sunday = forms.CharField(label="Sun", required=False)
        sundayH = forms.DecimalField(label="Hours",
                                     max_digits=12,
                                     min_value=0.0,
                                     max_value=24.0,
                                     decimal_places=2
                                     , required=False)

        total = forms.CharField(label="Total", required=False)
        totalH = forms.DecimalField(label="Hours",
                                    max_digits=12,
                                    min_value=0.0,
                                    decimal_places=2,
                                    widget=forms.HiddenInput()
                                    )

        tsId = forms.IntegerField(label="id",
                                  required=False, widget=forms.HiddenInput(),
                                  )
        is_internal = forms.IntegerField(label="is_internal",
                                         required=False, widget=forms.HiddenInput()
                                  )
        approved = forms.BooleanField(label="approved",
                                      required=False)
        hold = forms.BooleanField(label="hold",
                                  required=False)
        # managerFeedback = forms.CharField(label="Feedback", required=False)
        remarks = forms.CharField(label="Remarks", required=False, widget=forms.Textarea(attrs={'cols': 100, 'rows': 5}))

        def __init__(self, *args, **kwargs):
            super(TimeSheetEntryForm, self).__init__(*args, **kwargs)
            self.fields['project'].queryset = Project.objects.filter(
                #closed=False,
                endDate__gte=enddate,
                #endDate__gte=datetime.date.today(),
                id__in=ProjectTeamMember.objects.filter(
                    Q(member=currentUser.id) |
                    Q(project__projectManager=currentUser.id)
                ).values('project_id')
            ).order_by('name')
            hold_value = self.fields['hold'].initial or self.initial.get('hold') or \
                         self.fields['hold'].widget.value_from_datadict(self.data, self.files, self.add_prefix('hold'))
            if hold_value:
                self.fields['mondayH'].widget.attrs['readonly'] = True
                self.fields['tuesdayH'].widget.attrs['readonly'] = True
                self.fields['wednesdayH'].widget.attrs['readonly'] = True
                self.fields['thursdayH'].widget.attrs['readonly'] = True
                self.fields['fridayH'].widget.attrs['readonly'] = True
                self.fields['saturdayH'].widget.attrs['readonly'] = True
                self.fields['sundayH'].widget.attrs['readonly'] = True
                self.fields['totalH'].widget.attrs['readonly'] = True
            project_id = self.fields['project'].initial\
                         or self.initial.get('project') \
                         or self.fields['project'].widget.value_from_datadict(self.data, self.files, self.add_prefix('project'))
            if project_id:
                try:
                    project_obj = Project.objects.get(id=int(project_id))
                except:
                    project_obj = project_id
                self.fields['is_internal'].widget.attrs['data-prev_value'] = int(project_obj.internal)
                self.fields['is_internal'].widget.attrs['value'] = int(project_obj.internal)
                self.fields['chapter'].queryset = Chapter.objects.filter(book=project_obj.book)
                self.fields['task'].queryset = Task.objects.filter(projectType=project_obj.projectType, active=True)
            else:
                self.fields['is_internal'].widget.attrs['data-prev_value'] = 1
                self.fields['is_internal'].widget.attrs['value'] = 1
            self.fields['location'].queryset = OfficeLocation.objects.filter(
                active=True)
            # self.fields['project'].widget.attrs['required'] = "required"
            # self.fields['chapter'].widget.attrs['required'] = "required"
            # self.fields['task'].widget.attrs['required'] = "required"
            self.fields['project'].widget.attrs['required'] = True
            self.fields['location'].widget.attrs['required'] = True
            self.fields['chapter'].widget.attrs['required'] = True
            self.fields['task'].widget.attrs['required'] = True
            self.fields['project'].widget.attrs[
                'class'] = "form-control d-item \
                billable-select-project  required_fields set-empty"
            self.fields['tsId'].widget.attrs['class'] = "set-zero"
            self.fields['location'].widget.attrs['class'] = \
                "form-control required_fields  d-item set-zero"
            self.fields['chapter'].widget.attrs[
                'class'] = "form-control d-item b-chapter \
                remove-sel-options  required_fields set-zero"
            self.fields['task'].widget.attrs[
                'class'
            ] = "form-control d-item b-task  required_fields remove-sel-options set-zero"

            self.fields['mondayH'].widget.attrs[
                'class'
            ] = " form-control Mon-t  b-hours d-item set-zero"

            self.fields['tuesdayH'].widget.attrs[
                'class'
            ] = " form-control Tue-t b-hours d-item set-zero"

            self.fields['wednesdayH'].widget.attrs[
                'class'
            ] = " form-control Wed-t b-hours d-item set-zero"

            self.fields['thursdayH'].widget.attrs[
                'class'
            ] = "form-control Thu-t b-hours d-item set-zero"

            self.fields['fridayH'].widget.attrs[
                'class'
            ] = "form-control Fri-t b-hours d-item set-zero"

            self.fields['saturdayH'].widget.attrs[
                'class'
            ] = "form-control Sat-t b-hours d-item set-zero"

            self.fields['sundayH'].widget.attrs[
                'class'
            ] = "form-control Sun-t b-hours d-item set-zero"

            self.fields['is_internal'].widget.attrs[
                'class'
            ] = "form-control is_internal set-zero"

            self.fields['totalH'].widget.attrs[
                'class'
            ] = "form-control t-hours-hidden d-item set-zero"
            self.fields['remarks'].widget.attrs[
                'class'
            ] = 'remarks set-empty'
            self.fields['mondayH'].widget.attrs['value'] = 0
            self.fields['tuesdayH'].widget.attrs['value'] = 0
            self.fields['wednesdayH'].widget.attrs['value'] = 0
            self.fields['thursdayH'].widget.attrs['value'] = 0
            self.fields['fridayH'].widget.attrs['value'] = 0
            self.fields['saturdayH'].widget.attrs['value'] = 0
            self.fields['sundayH'].widget.attrs['value'] = 0
            self.fields['totalH'].widget.attrs['value'] = 0
            self.fields['tsId'].widget.attrs['value'] = 0
            # self.fields['is_internal'].widget.attrs['value'] = 0
            self.fields['projectType'].widget.attrs['value'] = 'Q'

    return TimeSheetEntryForm


# Form Class to create milestones for project
class changeProjectLeaderForm(forms.ModelForm):
    DeliveryManager = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        label="Delivery Manager",
        widget=autocomplete.ModelSelect2(url='AutocompleteUser', attrs={
            'data-placeholder': 'Type Delievery Manager Name ...',
        }
                                         # url='AutocompleteUser'
                                         ),
        )
    pmDelegate = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        label="PM Delegate",
        widget=autocomplete.ModelSelect2(url='AutocompleteUser', attrs={
            'data-placeholder': 'Type PM Delegate Name ...',
        }
                                         # url='AutocompleteUser'
                                         ),
        required=False, )
    class Meta:
        model = Project
        fields = ('projectManager', 'DeliveryManager', 'pmDelegate')
        widgets = {
            'projectManager': autocomplete.ModelSelect2Multiple()
        }

    def __init__(self, *args, **kwargs):
        super(changeProjectLeaderForm, self).__init__(*args, **kwargs)
        self.fields['projectManager'].widget.attrs['class'] = "form-control"
        self.fields['pmDelegate'].widget.attrs['class'] = "form-control"
        self.fields['DeliveryManager'].widget.attrs['class'] = "form-control"


# Form Class to create project
class ProjectBasicInfoForm(changeProjectLeaderForm, forms.ModelForm):

    projectFinType = forms.ChoiceField(choices=PROJECTFINTYPE, required=True,
                                       label=('Project Fin Type'), )
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

    DeliveryManager = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        label="Delivery Manager",
        widget=autocomplete.ModelSelect2(url='AutocompleteUser', attrs={
            'data-placeholder': 'Type Delievery Manager Name ...',
        }
            # url='AutocompleteUser'
        ),
        required=True, )
    pmDelegate = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        label="PM Delegate",
        widget=autocomplete.ModelSelect2(url='AutocompleteUser', attrs={
            'data-placeholder': 'Type PM Delegate Name ...',
        }
                                         # url='AutocompleteUser'
                                         ),
        required=False, )

    customerContact = forms.EmailField(required=True)



    class Meta:
        model = Project
        fields = (
            'projectType',
            'projectFinType',
            'customer',
            'startDate',
            'endDate',
            'name',
            'bu',
            'customerContact',
            'book',
            'projectManager',
            'pmDelegate',
            'signed',
            'currentProject',

            )
        widgets = {
            'endDate': DateTimePicker(options=dateTimeOption),
            'startDate': DateTimePicker(options=dateTimeOption),
            'currentProject': forms.RadioSelect(
                choices=[(True, 'New Development'), (False, 'Revision')]
            ),
            'signed': forms.RadioSelect(
                choices=[(True, 'Yes'), (False, 'No')]
            ),
            'projectManager': autocomplete.ModelSelect2Multiple(attrs={'data-placeholder': 'Type Additional manager...'} ),

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
        self.fields['projectFinType'].widget.attrs['class'] = \
            "form-control"
        self.fields['projectManager'].widget.attrs['class'] = \
            "form-control coordinatorcount"
        self.fields['projectManager'].queryset = \
            User.objects.filter(is_active=True)
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
        self.fields['startDate'].widget.attrs['class'] = \
            "form-control"
        self.fields['endDate'].widget.attrs['class'] = \
            "form-control"



#Upload Form  fro project screen
class UploadForm(forms.ModelForm):
    Sowdocument = forms.FileField(label='Sow Attachment', required=False,help_text=mark_safe(
        "Allowed file types: jpg, csv, png, pdf, xls, xlsx, doc, docx, eml, jpeg.<br>Maximum allowed file size: 1MB"))
    Sowdocument.widget.attrs = {'class': 'filestyle', 'data-buttonBefore': 'true',
                                         'data-iconName': 'glyphicon glyphicon-paperclip'}

    Estimationdocument = forms.FileField(label='Estimation Attachment', required=False, help_text=mark_safe(
        "Allowed file types: jpg, csv, png, pdf, xls, xlsx, doc, docx, eml, jpeg.<br>Maximum allowed file size: 1MB"))
    Estimationdocument.widget.attrs = {'class': 'filestyle', 'data-buttonBefore': 'true',
                                'data-iconName': 'glyphicon glyphicon-paperclip'}

    class Meta:
        model = ProjectDetail
        fields = ('Sowdocument',
                    'Estimationdocument',
                  )

    def __init__(self, *args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)
        self.fields['Sowdocument'].widget.attrs['class'] = \
            "form-control"
        self.fields['Estimationdocument'].widget.attrs['class'] = \
            "form-control"

# Modify rejected Project


class RejectProjectForm(forms.ModelForm):

    class Meta:
        model = ProjectDetail
        id = forms.IntegerField(label="Project id", required=False, widget=forms.HiddenInput())
        fields = ('id',)




    def __init__(self, *args, **kwargs):
        super(RejectProjectForm, self).__init__(*args, **kwargs)
        # self.fields['project'].empty_label = None


class ModifyProjectInfoForm(forms.ModelForm):
    id = forms.IntegerField(label="BasicInfoId", widget=forms.HiddenInput())

    projectFinType = forms.ChoiceField(choices=PROJECTFINTYPE, required=True,
                                       label=('Project Fin Type'), )
    book = forms.ModelChoiceField(
        queryset=Book.objects.all(),
        label="Book/Title",
        widget=autocomplete.ModelSelect2(url='AutocompleteBook', attrs={
            # Set some placeholder
            'data-placeholder': 'Type Book/Title Name ...',
            # Only trigger autocompletion after 3 characters have been typed
            # 'data-minimum-input-length': 3,
        }, ),
        required=False, )

    DeliveryManager = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        label="Delivery Manager",
        widget=autocomplete.ModelSelect2(url='AutocompleteUser', attrs={
            'data-placeholder': 'Type Delievery Manager Name ...',
        }
                                         ),
        required=False, )
    practicename = forms.ModelChoiceField(
        queryset=Practice.objects.all(),
        label="Select Practice",
        widget=autocomplete.ModelSelect2(url='AutocompletePracticeName', attrs={
            'data-placeholder': 'Type Practice Name ...',
            'class': 'practicevalue',
        }, ),
        required=False, )

    pmDelegate = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        label="PM Delegate",
        widget=autocomplete.ModelSelect2(url='AutocompleteUser', attrs={
            'data-placeholder': 'Type PM Delegate Name ...',
        }
                                         ),
        required=False, )
    Sowdocument = forms.FileField(label='Sow Attachment', required=False, help_text=mark_safe(
        "Allowed file types: jpg, csv, png, pdf, xls, xlsx, doc, docx, eml, jpeg.<br>Maximum allowed file size: 1MB"))
    Sowdocument.widget.attrs = {'class': 'filestyle', 'data-buttonBefore': 'true',
                                'data-iconName': 'glyphicon glyphicon-paperclip'}

    Estimationdocument = forms.FileField(label='Estimation Attachment', required=False, help_text=mark_safe(
        "Allowed file types: jpg, csv, png, pdf, xls, xlsx, doc, docx, eml, jpeg.<br>Maximum allowed file size: 1MB"))
    Estimationdocument.widget.attrs = {'class': 'filestyle', 'data-buttonBefore': 'true',
                                       'data-iconName': 'glyphicon glyphicon-paperclip'}

    customerContact = forms.EmailField(required=False)

    class Meta:
        model = Project
        fields = (
            'id',
            'projectType',
            'projectFinType',
            'customer',
            'startDate',
            'endDate',
            'bu',
            'customerContact',
            'book',
            'plannedEffort',
            'totalValue',
            'salesForceNumber',
            'DeliveryManager',
            'projectManager',
            'pmDelegate',
            'signed',
            'currentProject',
            'Sowdocument',
            'Estimationdocument',


        )
        widgets = {
            'endDate': DateTimePicker(options=dateTimeOption),
            'startDate': DateTimePicker(options=dateTimeOption),
            'currentProject': forms.RadioSelect(
                choices=[(True, 'New Development'), (False, 'Revision')]
            ),
            'signed': forms.RadioSelect(
                choices=[(True, 'Yes'), (False, 'No')]),
            'projectManager': autocomplete.ModelSelect2Multiple(
                attrs={'data-placeholder': 'Type Additional manager...'}),

        }

    def __init__(self, *args, **kwargs):
        super(ModifyProjectInfoForm, self).__init__(*args, **kwargs)
        self.fields['projectType'].widget.attrs['class'] = \
            "form-control"
        self.fields['projectType'].queryset = \
            projectType.objects.filter(active=True).order_by('description')
        self.fields['bu'].queryset = \
            BusinessUnit.objects.all().order_by('name')
        self.fields['customer'].queryset = \
            Customer.objects.filter(active=True).order_by('name')
        self.fields['projectFinType'].widget.attrs['class'] = \
            "form-control"
        self.fields['projectManager'].widget.attrs['class'] = \
            "form-control coordinatorcount"
        self.fields['projectManager'].queryset = \
            User.objects.filter(is_active=True)
        self.fields['bu'].widget.attrs['class'] = \
            "form-control"
        self.fields['customer'].widget.attrs['class'] = \
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
        self.fields['startDate'].widget.attrs['class'] = \
            "form-control"
        self.fields['endDate'].widget.attrs['class'] = \
            "form-control"
        self.fields['id'].widget.attrs['class'] = \
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
    reason = forms.ChoiceField(choices=PROJECT_CLOSE_FLAG)
    remark = forms.CharField(max_length=100, required=False)

    class Meta:
        model = ProjectChangeInfo
        fields = (
            'reason', 'remark', 'startDate', 'endDate', 'revisedEffort',
            'revisedTotal', 'closed', 'signed', 'Sowdocument', 'estimationDocument',
        )
        widgets = {
            'endDate': DateTimePicker(options=dateTimeOption),
            'startDate': DateTimePicker(options=dateTimeOption),
        }

    def __init__(self, *args, **kwargs):
        super(ChangeProjectBasicInfoForm, self).__init__(*args, **kwargs)
        self.fields['id'].widget.attrs['value'] = 0
        self.fields['Sowdocument'].widget.attrs['class'] = "form-control Sowdocument"
        self.fields['reason'].widget.attrs['class'] = "form-control reason"
        self.fields['remark'].widget.attrs['class'] = "form-control remark controls"
        self.fields['endDate'].widget.attrs['class'] = "form-control"
        self.fields['revisedEffort'].widget.attrs['class'] = "form-control"
        self.fields['revisedTotal'].widget.attrs['class'] = "form-control"
        self.fields['closed'].widget.attrs['class'] = "form-control project_close"
        self.fields['signed'].widget.attrs['class'] = "form-control sowsigned"


class ChangeProjectTeamMemberForm(forms.ModelForm):
    id = forms.IntegerField(label="teamRecId",widget=forms.HiddenInput() )
    member = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        # label="Project Leader",
        widget=autocomplete.ModelSelect2(url='AutocompleteUser', attrs={
            # Set some placeholder
            'data-placeholder': 'Type Employee Name ...',
            'required': 'true'
            # Only trigger autocompletion after 3 characters have been typed
            # 'data-minimum-input-length': 3,
        }, ),
        required=True, )
    class Meta:
        model = ProjectTeamMember
        fields = (
            'member',
            'role',
            'product',
            'startDate',
            'plannedcount',
            'actualcount',
            'plannedEffort',
        )
        widgets = {
            'startDate': DateTimePicker(options=dateTimeOption),
            'project': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ChangeProjectTeamMemberForm, self).__init__(*args, **kwargs)
        self.fields['id'].widget.attrs['value'] = 0
        self.fields['plannedEffort'].widget.attrs['max'] = 40
        self.fields['plannedEffort'].widget.attrs[
            'required'] = "true"
        self.fields['id'].widget.attrs['class'] = "set-zero"
        self.fields['member'].widget.attrs['class'] = "form-control min-200"
        self.fields['startDate'].widget.attrs[
            'class'] = "form-control min-100 pro-start-date"
        # self.fields['endDate'].widget.attrs[
        #     'class'] = "form-control  min-100 pro-end-date"
        self.fields['startDate'].widget.attrs['required'] = True
        # self.fields['endDate'].widget.attrs['required'] = True
        self.fields['actualcount'].widget.attrs[
            'class'] = "form-control w-100 pro-planned-effort-percent"
        self.fields['actualcount'].widget.attrs[
            'required'] = "true"
        self.fields['plannedEffort'].widget.attrs[
            'class'] = "form-control w-100"


class CloseProjectMilestoneForm(forms.ModelForm):

    id = forms.IntegerField(label="msRecId", widget=forms.HiddenInput())
    name = forms.ModelChoiceField(
        queryset=Milestone.objects.all(),
        label="Select Milestone Name",
        required=False, )
    description = forms.CharField(required=False,)
    class Meta:
        model = ProjectMilestone
        fields = (
            'milestoneDate', 'name', 'description',
            'amount', 'closed'
        )
        widgets = {
            'project': forms.HiddenInput(),
            'milestoneDate': DateTimePicker(options=dateTimeOption),
            # 'MilestoneName': autocomplete.ModelSelect2(url='AutocompleteMilestonetype', attrs={
            # 'data-placeholder': 'Type Milestone Type...'})
        }

    def clean(self):
        submitted_value = super(CloseProjectMilestoneForm, self).clean()
        is_closed = submitted_value.get("closed")
        name = submitted_value.get("name")
        if not is_closed and not name:
            raise forms.ValidationError("milestone name is a required field.")
        return submitted_value


    def __init__(self, *args, **kwargs):
        super(CloseProjectMilestoneForm, self).__init__(*args, **kwargs)
        self.fields['id'].widget.attrs['value'] = 0
        self.fields['milestoneDate'].widget.attrs['class'] = \
            "date-picker d-item form-control"
        self.fields['description'].widget.attrs['class'] = "d-item input-item form-control"
        self.fields['name'].widget.attrs['class'] = "d-item input-item form-control"
        self.fields['amount'].widget.attrs['class'] = \
            "milestone-item-amount d-item input-item form-control"
        self.fields['closed'].widget.attrs['class'] = "form-control"
        self.fields['amount'].widget.attrs['style'] = "width: inherit;"


# Project Flag Form
class ProjectFlagForm(forms.ModelForm):
    SopLink = forms.CharField(label=('Sop Link'), required=False)
    Discipline = forms.ModelChoiceField(
        queryset=DataPoint.objects.all(),
        label="Select Discipline",
        widget=autocomplete.ModelSelect2(url='AutocompleteDatapointName', attrs={
            'data-placeholder': 'Type Discipline Name ...',
            'class': 'practicevalue',
        }, ),
        required=False, )
    projecttemplate = forms.ModelChoiceField(
        queryset=ProjectSopTemplate.objects.all(),
        label="Select Process template",
        widget=autocomplete.ModelSelect2(url='Autocompleteprojecttemplate', attrs={
            'data-placeholder': 'Type Template Name ...',
            'class': 'ProjectSopTemplate',
        }, ),
        required=True, )

    projectasset = forms.ModelChoiceField(
        queryset=ProjectAsset.objects.all(),
        label="Select project Asset",
        widget=autocomplete.ModelSelect2(url='AutocompleteProjectAsset', attrs={
            'data-placeholder': 'Type Asset Name ...',
            'class': 'projectasset',
        }, ),
        required=False, )


    sopname = forms.ModelChoiceField(
        queryset=qualitysop.objects.all(),
        label="Select QualitySOP",
        widget=autocomplete.ModelSelect2(url='AutocompleteQualitySOP', attrs={
            'data-placeholder': 'Type  QualitySOP Name ...',
        }, ),
        required=False, )

    ProjectScope = forms.ModelChoiceField(
        queryset=ProjectScope.objects.all(),
        label="Select Project Scope",
        widget=autocomplete.ModelSelect2(url='Autocompleteprojectscope', attrs={
            'data-placeholder': 'Type  Project Scope Name ...',
        }, ),
        required=False, )

    outsource_contract_value = forms.DecimalField(initial=0.0, required=False)

    class Meta:
        model = Project
        fields = (
            'plannedEffort',
            'totalValue',
            'po',
            'salesForceNumber',
            'sopname',
            'SopLink',
            'projecttemplate',
            'Discipline',
            'projectasset',
            'ProjectScope',

        )

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
        self.fields['plannedEffort'].widget.attrs['min'] = 8
        self.fields['projectasset'].widget.attrs['class']= "total-value-input form-control"
        self.fields['SopLink'].widget.attrs['id'] = "soplink"
        self.fields['SopLink'].widget = forms.HiddenInput()
        self.fields['sopname'].widget.attrs['class']="sopname"


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
    project = forms.ModelChoiceField(
        queryset=Project.objects.all().order_by('name'),
        # label="Book/Title",
        widget=autocomplete.ModelSelect2(url='AutocompleteProjects', attrs={
            'data-placeholder': 'Enter a Project Name /Project Id ...',
        }, ), required=False,)
    member = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=autocomplete.ModelSelect2(url='AutocompleteUser', attrs={
            'data-placeholder': 'Type Employee Name ...',
        }, ), required=True, )

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
        pmflag = kwargs.pop('pmvalue')
        super(ProjectPerfomanceReportForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.filter(
            id__in=helper.get_my_project_list(currentUser, pmflag)).order_by('name')
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
        #import ipdb;ipdb.set_trace()
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
