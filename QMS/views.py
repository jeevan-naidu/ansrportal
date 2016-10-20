
from django.views.generic import View ,TemplateView
from django.shortcuts import render

from .forms import *
import logging
logger = logging.getLogger('MyANSRSource')


class AssessmentView(TemplateView):
    template_name = "ansrS_QA_Tmplt_Assessment (Non Platform) QA sheet_3.3.html"

    def get_context_data(self, **kwargs):
        context = super(AssessmentView, self).get_context_data(**kwargs)

        form = BaseAssessmentTemplateForm()
        context['form'] = form

        return context

    def post(self, request):
        form = BaseAssessmentTemplateForm(request.POST)
        if form.is_valid():
            active_tab = form.cleaned_data['active_tab']
            project = form.cleaned_data['project']
            chapter =form.cleaned_data['chapter']
            author =form.cleaned_data['author']

        return render(self.request, self.template_name, {'form': form})
