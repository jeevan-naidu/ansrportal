from django import forms
from .models import *
from django.contrib.auth.models import User
from MyANSRSource.models import Project, Chapter


from dal import autocomplete


#
# class AssignProjectMember(forms.Form):
#     project = forms.ModelChoiceField(
#                 queryset=Project.objects.all(),
#                 widget=autocomplete.ModelSelect2(url='AutocompleteProjects', attrs={
#                  'data-placeholder': 'Type project Name ...',
#         }, ),
#                 required=True, )
#     template = forms.ModelChoiceField(
#                 queryset=TemplateMaster.objects.all(),
#                 widget=autocomplete.ModelSelect2(url='AutocompleteTemplates', attrs={
#                  'data-placeholder': 'Type Template Name ...',
#         }, ),
#                 required=True, )
#     qms_process_model = forms.ModelChoiceField(
#                 queryset=QMSProcessModel.objects.all(),
#                  ),
#
#     author = forms.ModelChoiceField(
#             queryset=User.objects.all(),
#             widget=autocomplete.ModelSelect2(url='AutoCompleteAssignUserProjectSpecific', forward=('project',),attrs={
#              'data-placeholder': 'Type Author Name ...',
#     }, ),
#             required=True, )
#     ER = forms.ModelChoiceField(
#             queryset=User.objects.all(),
#             widget=autocomplete.ModelSelect2(url='AutoCompleteAssignUserProjectSpecific', forward=('project',),attrs={
#              'data-placeholder': 'Type EA Name ...',
#     }, ),
#             required=True, )
#
#     EA = forms.ModelChoiceField(
#             queryset=User.objects.all(),
#             widget=autocomplete.ModelSelect2(url='AutoCompleteAssignUserProjectSpecific', forward=('project',),attrs={
#              'data-placeholder': 'Type EA Name ...',
#     }, ),
#             required=True, )
#
#     CE = forms.ModelChoiceField(
#             queryset=User.objects.all(),
#             widget=autocomplete.ModelSelect2(url='AutoCompleteAssignUserProjectSpecific', forward=('project',),attrs={
#              'data-placeholder': 'Type CE Name ...',
#     }, ),
#             required=True, )
#
#     QA = forms.ModelChoiceField(
#             queryset=User.objects.all(),
#             widget=autocomplete.ModelSelect2(url='AutoCompleteAssignUserProjectSpecific', forward=('project',), attrs={
#              'data-placeholder': 'Type QA Name ...',
#     }, ),
#             required=True, )



class BaseAssessmentTemplateForm(forms.Form):
    project = forms.ModelChoiceField(
                queryset=Project.objects.all(),
                widget=autocomplete.ModelSelect2(url='AutocompleteProjects', attrs={
                 'data-placeholder': 'Type project Name ...',
        }, ),
                required=True, )

    chapter = forms.ModelChoiceField(
            queryset=Chapter.objects.all(),
            widget=autocomplete.ModelSelect2(url='AutocompleteChapters', forward=('project',), attrs={
             'data-placeholder': 'Type Chapter Name...',
    }, ),
            required=True, )
    author = forms.ModelChoiceField(
            queryset=User.objects.all(),
            widget=autocomplete.ModelSelect2(url='AutoCompleteUserProjectSpecific', forward=('project', 'chapter'),attrs={
             'data-placeholder': 'Type Author Name ...',
    }, ),
            required=True, )

    class Meta:
        model = QASheetHeader
        fields = ('project', 'chapter', 'author',)

    def __init__(self, *args, **kwargs):
        super(BaseAssessmentTemplateForm, self).__init__(*args, **kwargs)
        #     # self.fields['project'].queryset = Project.objects.all()
        #     #
        #     # project_id = self.fields['project'].initial\
        #     #              or self.initial.get('project') \
        #     #              or self.fields['project'].widget.value_from_datadict\
        #     #                  (self.data, self.files, self.add_prefix('project'))
        #     # if project_id:
        #     #     try:
        #     #         project_obj = Project.objects.get(id=int(project_id))
        #     #     except:
        #     #         project_obj = project_id
        # #     self.fields['chapter'].queryset = Chapter.objects.filter(book=project_obj.book)
        self.fields['project'].widget.attrs['class'] = "filter_form"
        self.fields['chapter'].widget.attrs['class'] = "filter_form"
        self.fields['author'].widget.attrs['class'] = "filter_form"


class ChooseMandatoryTabsForm(BaseAssessmentTemplateForm):
    qms_process_model = forms.ModelChoiceField(
        queryset=QMSProcessModel.objects.all(),
        widget=autocomplete.ModelSelect2(url='AutocompleteProcessModel', attrs={
            'data-placeholder': 'Type Process Model Name ...',
        }, ),
        required=True, )
    template = forms.ModelChoiceField(
        queryset=TemplateMaster.objects.all(),
        widget=autocomplete.ModelSelect2(url='AutocompleteTemplates', attrs={
            'data-placeholder': 'Type Template Name ...',
        }, ),
        required=True, )
    review_group = forms.ModelMultipleChoiceField(queryset=ReviewGroup.objects.all(),
                                                  widget=forms.CheckboxSelectMultiple(), required=False)
    author = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(url='AutoCompleteAssignUserProjectSpecific', forward=('project', 'chapter'),
                                         attrs={
                                             'data-placeholder': 'Type Author Name ...',
                                         }, ),
        required=True, )

    def __init__(self, *args, **kwargs):
        super(ChooseMandatoryTabsForm, self).__init__(*args, **kwargs)
        # self.field_order['process_model', 'template', 'review_group', 'project', 'chapter', 'author']


def review_report_base(template_id, project_id):
    class ReviewReportForm(forms.Form):
        review_item = forms.CharField()
        qms_id = forms.IntegerField(label="id",
                                  required=False,
                                  widget=forms.HiddenInput())
        defect = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 30}))

        severity_type = forms.ModelChoiceField(widget=forms.Select(),
                                               queryset=DefectTypeMaster.objects.all(), )
        # defect_severity_level = forms.CharField()
        # defect_classification = forms.CharField()

        severity_level = forms.ModelChoiceField(widget=forms.Select(),
                                                queryset=SeverityLevelMaster.objects.all(),required=False, )
        defect_classification = forms.ModelChoiceField(widget=forms.Select(),
                                                queryset=DefectClassificationMaster.objects.all(),required=False, )
        severity_level = forms.ModelChoiceField(widget=forms.Select(),
                                                queryset=SeverityLevelMaster.objects.all(),required=False, )
        defect_classification = forms.ModelChoiceField(widget=forms.Select(),
                                                queryset=DefectClassificationMaster.objects.all(),required=False, )

        is_fixed = forms.CharField(required=False,)
        fixed_by = forms.CharField(required=False,)
        remarks = forms.CharField(required=False,)

        class Meta:
            model = ReviewReport
            fields = ('review_item', 'defect', 'is_fixed', 'fixed_by', 'remarks', 'qms_id')

        def __init__(self, *args, **kwargs):
            super(ReviewReportForm, self).__init__(*args, **kwargs)
            self.fields['severity_type'].widget.attrs['class'] = 'defect'
            template_obj = ProjectTemplateProcessModel.objects.get(project=project_id)
            defect_type_master_obj = DefectSeverityLevel.objects.filter(template=template_obj.template)
            # print defect_type_master_obj
            # self.fields['severity_type'].queryset = DefectTypeMaster.objects.all()
            self.fields['qms_id'].widget.attrs['class'] = "set-zero"
            self.fields['qms_id'].widget.attrs['value'] = 0
            # self.fields['severity_type'].queryset = DefectTypeMaster.objects.filter\
            #     (id__in=defect_type_master_obj.severity_type)
            # self.fields['defect_severity_level'].widget.attrs['disabled'] = True
            self.fields['is_fixed'].widget.attrs['readonly'] = True
            self.fields['fixed_by'].widget.attrs['readonly'] = True
            # self.fields['severity_level'].queryset = SeverityLevelMaster.objects.all()
            # self.fields['severity_level'].queryset = SeverityLevelMaster.objects.filter\
            #     (id=defect_type_master_obj.severity_level)
            # self.fields['defect_classification'].queryset = DefectClassificationMaster.objects.all()
            # self.fields['defect_classification'].queryset = DefectClassificationMaster.objects.filter\
            #     (id=defect_type_master_obj.defect_classification)
            # print DefectClassificationMaster.objects.filter(id__in=defect_type_master_obj)
            self.fields['defect_classification'].widget.attrs['disabled'] = True
            self.fields['severity_level'].widget.attrs['disabled'] = True
            # print defect_type_master_obj
            # self.fields['severity_type'].queryset = DefectTypeMaster.filter(id__in=[defect_type_master_obj])
            # severity_type_id = self.fields['severity_type'].initial\
            #              or self.initial.get('severity_type') \
            #              or self.fields['severity_type'].widget.value_from_datadict\
            #                  (self.data, self.files, self.add_prefix('severity_type'))
            # if severity_type_id:
            #     severity_type_obj = defect_type_master_obj.filter(severity_type=severity_type_id)
            #
            #     self.fields['severity_level'].queryset = SeverityLevelMaster.objects.filter\
            #     (id=defect_type_master_obj.severity_level)
            #     self.fields['defect_classification'].queryset = DefectClassificationMaster.objects.filter\
            #         (id__in=severity_type_obj.defect_classification)

    return ReviewReportForm


