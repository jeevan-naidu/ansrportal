
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
                obj = QASheetHeader.objects.get(project=project, chapter=chapter, author=author)
                template_obj = get_object_or_404(ProjectTemplate, project=obj.project)
                template_id = template_obj.id
                request.session['pk'] = obj.id
                request.session['project'] = project
                request.session['chapter'] = chapter
                request.session['author'] = author
                request.session['active_tab'] = active_tab
                defect_master = DefectTypeMaster.objects.all()
                try:
                    reports = ReviewReport.objects.filter(QA_sheet_header=obj.id).values(
                        'review_item', 'defect', 'defect_severity_level__severity_type',
                        'defect_severity_level__severity_level', 'defect_severity_level__defect_classification',
                        'is_fixed', 'fixed_by__username', 'remarks')

                except reports.ObjectDoesNotExist, e:
                    print "error " + str(e)
                    reports = None
                    template_id = None

            except ObjectDoesNotExist:
                messages.error(self.request, "Sorry No Records Found")
        else:
            form = BaseAssessmentTemplateForm()
        qms_form = review_report_base(template_id, obj.project)

        qmsData = {}
        qmsDataList = []
        for eachData in reports:
            for k, v in eachData.iteritems():
                qmsData[k] = v
                if k == 'review_item':
                    qmsData['review_item'] = v

                if k == 'defect':
                    qmsData['defect'] = v

                if k == 'defect_severity_level__severity_type':
                    qmsData['severity_type'] = v

                if k == 'defect_severity_level__severity_level':
                    qmsData['severity_level'] = v

                if k == 'defect_severity_level__defect_classification':
                    qmsData['defect_classification'] = v

                if k == 'is_fixed':
                    qmsData['is_fixed'] = v

                if k == 'fixed_by__username':
                    qmsData['fixed_by'] = v

                if k == 'remarks':
                    qmsData['remarks'] = v
            # print qmsData
            qmsDataList.append(qmsData.copy())

        qmsData.clear()
        # print qmsDataList
        qms_formset = formset_factory(
            qms_form, extra=3, max_num=10, can_delete=True
        )

        qms_formset = qms_formset(initial=qmsDataList)
        return render(self.request, self.template_name, {'form': form, 'defect_master': defect_master,
                                                         'reports': reports, 'review_formset': qms_formset,
                                                         'template_id': template_id})


class ReviewReportManipulationView(View) :
    def post(self, request):
        qmsData = {}
        qmsDataList = []
        form = BaseAssessmentTemplateForm(request.POST)
        if form.is_valid():
            for form_data in form:
                if form_data.cleaned_data['DELETE'] is True:
                    ReviewReport.object.filter(id=form_data.cleaned_data['id']).update(is_active=False)
                for k, v in form.cleaned_data.iteritems():
                    qmsData[k] = v
                qmsDataList.append(qmsData.copy())
                qmsData.clear()




class AssessmentReviewCreateView(CreateView):
    model = ReviewReport
    template_name_suffix = '_create_form'
    fields = ['review_item', 'defect', 'defect_severity_level', 'is_fixed', 'fixed_by']

    def form_valid(self, form):
        form.instance.project_chapter_reviewer_relationship = self.request.session['pk']
        return super(ReviewReport, self).form_valid(form)


class AssessmentReviewEditView(UpdateView):
    model = ReviewReport
    template_name_suffix = '_update_form'
    fields = ['review_item', 'defect', 'defect_severity_level', 'is_fixed', 'fixed_by']

    def form_valid(self, form):
        form.instance.project_chapter_reviewer_relationship = self.request.session['pk']
        return super(ReviewReport, self).form_valid(form)


def fetch_severity(request):

    template_id = request.GET.get('template_id')
    severity = request.GET.get('severity_type')
    obj = DefectSeverityLevel.objects.get(template=template_id, severity_type=severity)
    context_data = {'severity_level': str(obj.severity_level), 'defect_classification': str(obj.defect_classification)}

    return HttpResponse(
            json.dumps(context_data),
            content_type="application/json"
        )