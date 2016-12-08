from django import forms
from .models import *
from django.contrib.auth.models import User
from MyANSRSource.models import Project, Chapter, ProjectManager


from dal import autocomplete


class BaseAssessmentTemplateForm(forms.Form):
    project = forms.ModelChoiceField(
                queryset=Project.objects.all(),
                widget=autocomplete.ModelSelect2(url='AutocompleteProjects', attrs={
                 'data-placeholder': 'Project ',
        }, ),
                required=True, )

    chapter = forms.ModelChoiceField(
            queryset=Chapter.objects.all(),
            widget=autocomplete.ModelSelect2(url='AutocompleteChapters', forward=('project',), attrs={
             'data-placeholder': 'Chapter ',
    }, ),
            required=True, )

    component = forms.ModelChoiceField(
        queryset=ComponentMaster.objects.all(),
        widget=autocomplete.ModelSelect2(url='AutoCompleteChapterSpecificComponent', forward=('project', 'chapter',),
                                         attrs={
                                             'data-placeholder': 'Component ',
                                         }, ),
        required=True, )

    author = forms.ModelChoiceField(
            queryset=User.objects.all(),
            widget=autocomplete.ModelSelect2(url='AutoCompleteUserProjectSpecific', forward=('project', 'chapter'),attrs={
             'data-placeholder': 'Author ',
    }, ),
            required=True, )

    class Meta:
        model = QASheetHeader
        fields = ('project', 'chapter', 'author', 'component', 'order_number')

    def __init__(self, *args, **kwargs):
        super(BaseAssessmentTemplateForm, self).__init__(*args, **kwargs)
        # user = kwargs.pop('user', None)
        # print user
        # self.fields['project'].queryset = Project.objects.filter(
        #     id__in=ProjectManager.objects.filter(
        #         user=user
        #     ).values('project')
        # )
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
        self.fields['project'].widget.attrs['class'] = " reset_field filter_form"
        self.fields['chapter'].widget.attrs['class'] = "reset_field filter_form"
        self.fields['author'].widget.attrs['class'] = " reset_field filter_form author_dropdown"
        self.fields['project'].widget.attrs['required'] = True
        self.fields['chapter'].widget.attrs['required'] = True
        self.fields['author'].widget.attrs['required'] = True
        self.fields['component'].widget.attrs['class'] = "filter_form reset_field"
        self.fields['component'].widget.attrs['required'] = True


class ChooseMandatoryTabsForm(BaseAssessmentTemplateForm):
    qms_process_model = forms.ModelChoiceField(
        queryset=QMSProcessModel.objects.all(),
        widget=autocomplete.ModelSelect2(url='AutocompleteProcessModel', forward=('project',), attrs={
            'data-placeholder': 'Process Model ',
        }, ),
        required=True, )
    template = forms.ModelChoiceField(
        queryset=TemplateMaster.objects.all(),
        widget=autocomplete.ModelSelect2(url='AutocompleteTemplates', forward=('project', 'qms_process_model'), attrs={
            'data-placeholder': 'Template ',
        }, ),
        required=True, )
    # review_group = forms.ModelMultipleChoiceField(queryset=ReviewGroup.objects.all(),
    #                                               widget=forms.CheckboxSelectMultiple(), required=False)
    component = forms.ModelChoiceField(
        queryset=ComponentMaster.objects.all(),
        widget=autocomplete.ModelSelect2(url='AutocompleteComponents',
                                         attrs={
                                             'data-placeholder': 'Component',
                                         }, ), required=True, )
    # author = forms.ModelChoiceField(
    #     queryset=User.objects.all(),
    #     widget=autocomplete.ModelSelect2(url='AutoCompleteAssignUserProjectSpecific', forward=('project', 'chapter'),
    #                                      attrs={
    #                                          'data-placeholder': 'Author',
    #                                      }, ),
    #     required=True, )
    # author = forms.ModelChoiceField(widget=forms.Select(), queryset=User.objects.none())
    author = forms.ModelChoiceField(widget=forms.Select(), queryset=User.objects.filter(is_active=True))

    def __init__(self, *args, **kwargs):
        # print"init"
        super(ChooseMandatoryTabsForm, self).__init__(*args, **kwargs)
        # self.fields['author'].widget.attrs['class'] = 'author_dropdown'
        self.fields['author'].widget.attrs['disabled'] = True

        self.fields['qms_process_model'].widget.attrs['class'] = 'reset_field author_dropdown '
        self.fields['template'].widget.attrs['class'] = 'reset_field author_dropdown'
        self.fields['qms_process_model'].widget.attrs['required'] = True
        self.fields['template'].widget.attrs['required'] = True

        # project_id_field = self.fields['project'].initial \
        #                    or self.initial.get('project') \
        #                    or self.fields['project'].widget.value_from_datadict(self.data, self.files,
        #                                                                         self.add_prefix('project'))
        # print"project" , project_id_field
        # if project_id_field:
        #     print "if"
        #     try:
        #         project_obj = Project.objects.get(id=int(project_id_field))
        #     except:
        #         project_obj = project_id_field
        #     self.fields['author'].queryset = ProjectTeamMember.objects.filter(project=project_obj,
        #                                                                       member__is_active=True)
        # else:
        #     print "else"
        #     self.fields['author'].queryset = User.objects.filter(is_active=True)
        # # self.field_order['process_model', 'template', 'review_group', 'project', 'chapter', 'author']


def review_report_base(template_id, project_id):
    class ReviewReportForm(forms.Form):
        review_item = forms.CharField()
        qms_id = forms.IntegerField(label="id",
                                  required=False,
                                  widget=forms.HiddenInput())
        defect = forms.CharField(required=False, )

        severity_type = forms.ModelChoiceField(widget=forms.Select(),
                                               queryset=DefectTypeMaster.objects.all(), )
        # defect_severity_level = forms.CharField()
        # defect_classification = forms.CharField()

        severity_level = forms.ModelChoiceField(widget=forms.Select(),
                                                queryset=SeverityLevelMaster.objects.all(),required=False, )

        defect_classification = forms.ModelChoiceField(widget=forms.Select(),
                                                queryset=DefectClassificationMaster.objects.all(),required=False, )

        is_fixed = forms.ChoiceField(required=False, choices=fixed_status, )
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
            # project_id_field = self.fields['project'].initial \
            #                    or self.initial.get('project') \
            #                    or self.fields['project'].widget.value_from_datadict(self.data, self.files,
            #                                                                         self.add_prefix('project'))
            # if project_id_field:
            #
            #     if project_id:
            #         try:
            #             project_obj = Project.objects.get(id=int(project_id_field))
            #         except:
            #             project_obj = project_id_field
            #         self.fields['author'].queryset = ProjectTeamMember.objects.filter(project=project_obj).values(
            #             'member_id')
            # print self.fields['author'].queryset
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
            # self.fields['author'].widget.attrs['class'] = 'author_dropdown'

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


