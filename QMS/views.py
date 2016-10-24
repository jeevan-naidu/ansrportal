
from django.views.generic import View , TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import render
from django.contrib import messages


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
        form = BaseAssessmentTemplateForm()
        reports = None
        if form.is_valid():
            form = BaseAssessmentTemplateForm(request.POST)
            active_tab = form.cleaned_data['active_tab']
            project = form.cleaned_data['project']
            chapter = form.cleaned_data['chapter']
            author = form.cleaned_data['author']
            try:
                obj = ProjectChapterReviewerRelationship.objects.get(project=project, chapter=chapter, author=author)
                request.session['pk'] = obj.id
                request.session['project'] = project
                request.session['chapter'] = chapter
                request.session['author'] = author
                request.session['active_tab'] = active_tab
                try:
                    reports = ReviewerReport.objects.filter(project_chapter_reviewer_relationship = obj.id)
                except reports.ObjectDoesNotExist:
                    reports = None

            except obj.ObjectDoesNotExist:
                messages.error(self.request, "Sorry The Project Doesn't Exist")

        return render(self.request, self.template_name, {'form': form, 'reports': reports})


class AssessmentReviewCreateView(CreateView):
    model = ReviewerReport
    template_name_suffix = '_create_form'
    fields = ['review_item', 'defect', 'defect_severity_level', 'is_fixed', 'fixed_by']

    def form_valid(self, form):
        form.instance.project_chapter_reviewer_relationship = self.request.session['pk']
        return super(ReviewerReport, self).form_valid(form)


class AssessmentReviewEditView(UpdateView):
    model = ReviewerReport
    template_name_suffix = '_update_form'
    fields = ['review_item', 'defect', 'defect_severity_level', 'is_fixed', 'fixed_by']

    def form_valid(self, form):
        form.instance.project_chapter_reviewer_relationship = self.request.session['pk']
        return super(ReviewerReport, self).form_valid(form)
