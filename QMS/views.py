
from django.views.generic import View , TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import render
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponseRedirect, HttpResponse
import json
from .forms import *
from django.forms.formsets import formset_factory
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
        reports = None

        if form.is_valid():

            active_tab = request.POST.get('active_tab')
            project = form.cleaned_data['project']
            chapter = form.cleaned_data['chapter']
            author = form.cleaned_data['author']
            try:
                obj = ProjectChapterReviewerRelationship.objects.get(project=project, chapter=chapter, author=author)
                template_obj = get_object_or_404(ProjectTemplate, project=obj.project)
                template_id = template_obj.id
                request.session['pk'] = obj.id
                request.session['project'] = project
                request.session['chapter'] = chapter
                request.session['author'] = author
                request.session['active_tab'] = active_tab
                defect_master = DefectTypeMaster.objects.all()
                try:
                    reports = ReviewerReport.objects.filter(project_chapter_reviewer_relationship=obj.id)
                    # print reports
                except reports.ObjectDoesNotExist, e:
                    print "error " + str(e)
                    reports = None
                    template_id = None

            except ObjectDoesNotExist :
                messages.error(self.request, "Sorry No Records Found")
        else:
            form = BaseAssessmentTemplateForm()
        qms_form = review_report_base(template_id, obj.project)
        qms_formset = formset_factory(
            qms_form, extra=5, max_num=10, can_delete=True
        )
        return render(self.request, self.template_name, {'form': form,'defect_master': defect_master,
                                                         'reports': reports, 'review_formset': qms_formset,
                                                         'template_id': template_id})


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


def fetch_severity(request):

    template_id = request.GET.get('template_id')
    severity = request.GET.get('severity_type')
    obj = DefectSeverityLevel.objects.get(template=template_id, severity_type=severity)
    context_data = {'severity_level': str(obj.severity_level), 'defect_classification': str(obj.defect_classification)}

    return HttpResponse(
            json.dumps(context_data),
            content_type="application/json"
        )