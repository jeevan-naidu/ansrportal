from django import forms
from .models import *
from django.contrib.auth.models import User
from MyANSRSource.models import Project, Chapter


from dal import autocomplete


class BaseAssessmentTemplateForm(forms.Form):
        project = forms.ModelChoiceField(
                queryset=User.objects.all(),
                widget=autocomplete.ModelSelect2(url='AutocompleteProjects', attrs={
                 'data-placeholder': 'Type project Name ...',
        }, ),
                required=True, )

        chapter = forms.ModelChoiceField(
                queryset=Chapter.objects.none(),
                widget=autocomplete.ModelSelect2(url='AutocompleteChapters', forward=('project',), attrs={
                 'data-placeholder': 'Select project Name  first...',
        }, ),
                required=True, )
        author = forms.ModelChoiceField(
                queryset=User.objects.all(),
                widget=autocomplete.ModelSelect2(url='AutocompleteUser', attrs={
                 'data-placeholder': 'Type Author Name ...',
        }, ),
                required=True, )

        class Meta:
            model = ProjectChapterReviewerRelationship
            fields = ('project', 'chapter', 'author',)
        #     widgets = {
        #      'chapter': autocomplete.ModelSelect2(url='AutocompleteChapters',
        #                                           forward=('project',), attrs={
        #          'data-placeholder': 'Please Select  Project ...',
        # },)
        # }

        def __init__(self, *args, **kwargs):
            super(BaseAssessmentTemplateForm, self).__init__(*args, **kwargs)
            self.fields['project'].queryset = Project.objects.all()

            project_id = self.fields['project'].initial\
                         or self.initial.get('project') \
                         or self.fields['project'].widget.value_from_datadict\
                             (self.data, self.files, self.add_prefix('project'))
            if project_id:
                try:
                    project_obj = Project.objects.get(id=int(project_id))
                except:
                    project_obj = project_id
                self.fields['chapter'].queryset = Chapter.objects.filter(book=project_obj.book)
            self.fields['project'].widget.attrs['class'] = "form-inline input-sm width-3"
            self.fields['project'].widget.attrs['class'] = "form-inline input-sm width-3"
            self.fields['project'].widget.attrs['class'] = "form-inline input-sm width-3"






