
from django.views.generic import View , TemplateView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.shortcuts import render
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponseRedirect, HttpResponse
import json
from .forms import *
from MyANSRSource.models import ProjectTeamMember
from django.forms.formsets import formset_factory
from django.core.urlresolvers import reverse
import logging
logger = logging.getLogger('MyANSRSource')


class ChooseTabs(FormView):
    template_name = 'reviewreport_create_form_1.html'
    form_class = ChooseMandatoryTabsForm
    success_url = ''

    def form_valid(self, form):
        ProjectTemplateProcessModel.objects.create(template=form.cleaned_data['template'],
                                                   project=form.cleaned_data['project'],
                                                   qms_process_model=form.cleaned_data['username'])

        for reviewer in form.cleaned_data['review_group']:
            QASheetHeader.objects.create(project=form.cleaned_data['project'], chapter=form.cleaned_data['chapter'],
                                         review_group=reviewer)

        return super(ChooseTabs, self).form_valid(form)


def get_review(obj):
    return ReviewReport.objects.filter(QA_sheet_header=obj.id, is_active=True).\
        values('id', 'review_item', 'defect', 'defect_severity_level__severity_type',
               'defect_severity_level__severity_level', 'defect_severity_level__defect_classification',
               'is_fixed', 'fixed_by__username', 'remarks')


def qa_sheet_header_obj(project, chapter, author, active_tab):
    try:
        result = QASheetHeader.objects.get(project=project, chapter=chapter, author=author,
                                           review_group=ReviewGroup.objects.get(id=active_tab))
        print result
    except ObjectDoesNotExist:
        result = None
    return result


def get_review_group():
    return ReviewGroup.objects.all()


def get_template_process_review(request):
    project = request.GET.get('project_id')
    template = request.GET.get('template_id')
    qms_process_model = request.GET.get('qms_process_model')
    tabs = {}
    tab_name = {}
    team_members = {}
    try:

        obj = TemplateProcessReview.objects.filter(template=template, qms_process_model=qms_process_model)
        members_obj = ProjectTeamMember.objects.filter(project=project)
        for members in members_obj:
            team_members[int(members.id)] = str(members.member.username)
        # print members_obj.query
        # print members_obj
        for ele in obj:
            tabs[str(ele.review_group)] = bool(ele.is_mandatory)
            tab_name[str(ele.review_group)] = int(ele.review_group.id)
    except ObjectDoesNotExist:
        tabs = team_members = tab_name = ''
    context_data = {'tabs': tabs, 'tab_name': tab_name, 'team_members': team_members}
    print context_data
    return HttpResponse(
        json.dumps(context_data),
        content_type="application/json"
    )


class AssessmentView(TemplateView):
    template_name = "ansrS_QA_Tmplt_Assessment (Non Platform) QA sheet_3.3.html"

    def get_context_data(self, **kwargs):
        context = super(AssessmentView, self).get_context_data(**kwargs)

        form = BaseAssessmentTemplateForm()
        context['form'] = form
        context['review_group'] = get_review_group()

        return context

    def post(self, request):
        form = BaseAssessmentTemplateForm(request.POST)
        # print request.POST
        reports = template_id = None
        active_tab = request.session['active_tab'] = request.POST.get('active_tab')
        if form.is_valid():

            project = form.cleaned_data['project']
            chapter = form.cleaned_data['chapter']
            author = form.cleaned_data['author']
            try:
                print "try"
                request.session['project'] = project
                request.session['chapter'] = chapter
                request.session['author'] = author
                obj = qa_sheet_header_obj(project, chapter, author, active_tab)
                # if obj is None:
                #     messages.error(self.request, "Sorry No Records Found")
                #     return HttpResponseRedirect(reverse('qms'))

                template_obj = get_object_or_404(ProjectTemplateProcessModel, project=obj.project)
                template_id = request.session['template_id'] = template_obj.id
                request.session['QA_sheet_header_id'] = obj.id
                defect_master = DefectTypeMaster.objects.all()
                try:
                    reports = get_review(obj)
                    # print reports
                    # request.session['reports'] = list(reports)

                except reports.ObjectDoesNotExist, e:
                    print "error " + str(e)
                    reports = None
                    request.session['template_id'] = template_id = None

            except ObjectDoesNotExist:
                messages.error(self.request, "Sorry No Records Found")
        else:
            form = BaseAssessmentTemplateForm()
        qms_form = review_report_base(template_id, project)

        qmsData = {}
        qmsDataList = []
        if len(reports) != 0:
            # print"im in"
            for eachData in reports:
                for k, v in eachData.iteritems():
                    qmsData[k] = v
                    if k == 'id':
                        qmsData['qms_id'] = v
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
            qms_form, max_num=1, can_delete=True
        )

        qms_formset = qms_formset(initial=qmsDataList)

        return render(self.request, self.template_name, {'form': form, 'defect_master': defect_master,
                                                         'reports': reports, 'review_formset': qms_formset,
                                                         'template_id': template_id,
                                                         'review_group': get_review_group(), 'questions': obj.count})


class ReviewReportManipulationView(AssessmentView):

    def post(self, request):
        # print request.POST
        print "im in formset post"
        fail = 0
        qmsData = {}
        qmsDataList = []
        request.session['active_tab'] = active_tab = request.POST.get('active_tab1')
        print request.POST.get('active_tab1')
        qms_form = review_report_base(request.session['template_id'], request.session['project'])
        qms_formset = formset_factory(
            qms_form,  max_num=1, can_delete=True
        )
        # my_post_dict = request.POST.copy()
        # my_post_dict['form-TOTAL_FORMS'] = 1
        # my_post_dict['form-INITIAL_FORMS'] = 2
        # my_post_dict['form-MAX_NUM_FORMS'] = 3
        # myformset = qms_formset(my_post_dict)
        q_form = qms_formset(request.POST)
        if q_form.is_valid():

            for form_elements in q_form:
                # print form_elements
                if form_elements.cleaned_data['DELETE'] is True:
                    # form_elements.cleaned_data['DELETE']
                    ReviewReport.objects.filter(id=form_elements.cleaned_data['qms_id']).update(is_active=False)
                else:
                    del(form_elements.cleaned_data['DELETE'])
                    for k, v in form_elements.cleaned_data.iteritems():
                        qmsData[k] = v
                    qmsDataList.append(qmsData.copy())
                    qmsData.clear()
                    # print qmsDataList
            for obj in qmsDataList:
                if obj['qms_id'] > 0:
                    report = ReviewReport.objects.get(id=obj['qms_id'])
                    # print obj['qms_id']
                else:
                    # print obj['qms_id']
                    report = ReviewReport()
                    report.created_by = request.user
                report.review_item = obj['review_item']
                report.defect = obj['defect']
                report.is_fixed = obj['is_fixed']
                report.remarks = obj['remarks']
                # print request.session['template_id']
                #
                # print request.session['active_tab']
                # print obj['severity_type']
                # import ipdb
                # ipdb.set_trace()
                defect_obj = DefectSeverityLevel.objects.get(template_id=request.session['template_id'],
                                                             severity_type=obj['severity_type'],
                                                             review_group_id=active_tab)
                # print defect_obj.query

                report.defect_severity_level = DefectSeverityLevel.objects.get(id=defect_obj.id)
                qa_obj = QASheetHeader.objects.get(id=request.session['QA_sheet_header_id'])
                report.QA_sheet_header = qa_obj
                report.updated_by = request.user
                try:
                    report.save()
                except Exception, e:
                    logger.error(" {0} ".format(str(e)))
                    fail += 1
                finally:
                    print request.POST.get('questions')
                    qa_obj.count = int(request.POST.get('questions'))
                    qa_obj.save()

        else:
            # print q_form.errors
            messages.error(request, q_form.errors)
            # context = {'form': BaseAssessmentTemplateForm(), 'review_formset': qms_formset}
        if fail == 0:
            messages.info(request, "successfully saved")
        else:
            messages.warning(request, "partially saved")

        return HttpResponseRedirect(reverse('qms'))
        obj = qa_sheet_header_obj(request.session['project'], request.session['chapter'], request.session['author'],
                                  active_tab)

        return render(self.request, "ansrS_QA_Tmplt_Assessment (Non Platform) QA sheet_3.3.html", {
            'form': BaseAssessmentTemplateForm(),
            'review_formset': qms_formset(request.POST), 'reports': get_review(obj), 'review_group': get_review_group()
        })


def fetch_severity(request):

    template_id = request.GET.get('template_id')
    severity = request.GET.get('severity_type')
    request.session['active_tab'] = request.GET.get('active_tab')
    obj = DefectSeverityLevel.objects.get(template=template_id, severity_type=severity)
    context_data = {'severity_level': str(obj.severity_level), 'defect_classification': str(obj.defect_classification)}

    return HttpResponse(
            json.dumps(context_data),
            content_type="application/json"
        )