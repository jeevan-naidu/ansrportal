from django import forms
from .models import *
from django.contrib.auth.models import User
from MyANSRSource.models import Project, Chapter


from dal import autocomplete


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
        model = ProjectChapterReviewerRelationship
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
        # self.fields['project'].widget.attrs['class'] = "form-inline input-sm width-3"
        # self.fields['project'].widget.attrs['class'] = "form-inline input-sm width-3"
        # self.fields['project'].widget.attrs['class'] = "form-inline input-sm width-3"


def review_report_base(template_id, project):
    class ReviewReportForm(forms.Form):
        severity_type = forms.ModelChoiceField(widget=forms.Select(),
                                               queryset=DefectTypeMaster.objects.all(), )
        severity_level = forms.ModelChoiceField(widget=forms.Select(),
                                               queryset=SeverityLevelMaster.objects.none(), )
        defect_classification = forms.ModelChoiceField(widget=forms.Select(),
                                               queryset=DefectClassificationMaster.objects.none(), )

        class Meta:
            model = ProjectChapterReviewerRelationship
            fields = ('review_item', 'defect', 'is_fixed')

        def __init__(self, *args, **kwargs):
            super(ReviewReportForm, self).__init__(*args, **kwargs)
            self.fields['severity_type'].widget.attrs['class'] = 'defect'
            # defect_type_master_obj = DefectSeverityLevel.objects.filter(template=template_id)
            # print defect_type_master_obj
            # self.fields['severity_type'].queryset = defect_type_master_obj
            # severity_type_id = self.fields['severity_type'].initial\
            #              or self.initial.get('severity_type') \
            #              or self.fields['severity_type'].widget.value_from_datadict\
            #                  (self.data, self.files, self.add_prefix('severity_type'))
            #
            # severity_type_obj = defect_type_master_obj.filter(severity_type=severity_type_id)
            #
            # self.fields['severity_level'].queryset = self.fields['defect_classification'].queryset =  severity_type_obj

    return ReviewReportForm


