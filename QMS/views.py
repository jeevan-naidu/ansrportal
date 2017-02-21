from django.views.generic import View , TemplateView ,ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponseRedirect, HttpResponse
import json
import datetime
from django.shortcuts import render
from .forms import *
from MyANSRSource.models import ProjectTeamMember
from django.forms.formsets import formset_factory
from django.core.urlresolvers import reverse, reverse_lazy
import logging
logger = logging.getLogger('MyANSRSource')
import os.path


try:
    dict.iteritems
except AttributeError:
    # Python 3
    def itervalues(d):
        return iter(d.values())

    def iteritems(d):
        return iter(d.items())
else:
    # Python 2
    def itervalues(d):
        return d.itervalues()

    def iteritems(d):
        return d.iteritems()


class ChooseTabs(FormView):
    template_name = 'reviewreport_create_form_1.html'
    form_class = ChooseMandatoryTabsForm
    success_url = reverse_lazy('choose_tabs')

    def form_valid(self, form):
        user_tab = {}
        order_number = {}
        # print self.request.POST
        users = {k: v for k, v in self.request.POST.items() if k.startswith('user_')}
        order = {k: v for k, v in self.request.POST.items() if k.startswith('order_')}
        # print users
        for k, v in users.iteritems():
            tab_id = k.split('_')
            user_tab[tab_id[1]] = v

        for k, v in order.iteritems():
            order_id = k.split('_')
            print v
            if v:
                v = int(v)
            if v and v != 0:
                order_number[order_id[1]] = v
            else:
                print 'else'
                messages.error(self.request, 'Order Number Cannot Be 0')
                return super(ChooseTabs, self).form_valid(form)

        # {u'user_3': u'256', u'user_1': u'255'}
        print users
        print order

        try:
            ProjectTemplateProcessModel.objects.get_or_create(template=form.cleaned_data['template'],
                                                              project=form.cleaned_data['project'],
                                                              qms_process_model=form.cleaned_data['qms_process_model'],
                                                              created_by=self.request.user)
        except Exception as e:
            print (str(e))
            logger.error(" {0} ".format(str(e)))

        cm_obj, chapter_component = ChapterComponent.objects.get_or_create(chapter=form.cleaned_data['chapter'],
                                                                           component=form.cleaned_data['component'],
                                                                           created_by=self.request.user, )

        # print cm_obj
        # print chapter_component
        # print user_tab
        for k, v in user_tab.iteritems():
            # print form.cleaned_data['author']
            # k = int(k)
            print k, order_number[k]
            obj, created = QASheetHeader.objects.update_or_create(project=form.cleaned_data['project'],
                                                                  chapter=form.cleaned_data['chapter'],
                                                                  author=form.cleaned_data['author'],
                                                                  chapter_component=cm_obj,
                                                                  review_group_id=int(k),
                                                                  defaults={'reviewed_by_id': int(v),
                                                                            'created_by': self.request.user,
                                                                            'order_number': order_number[k]}, )
            # print obj, created
            if not created:
                obj.updated_by = self.request.user
        messages.info(self.request, "Successfully Saved")
        return super(ChooseTabs, self).form_valid(form)


def get_review(obj):
    try:
        s = ReviewReport.objects.filter(QA_sheet_header=obj.id, is_active=True). \
            values('id', 'review_item', 'defect', 'defect_severity_level__severity_type',
                   'defect_severity_level__severity_level', 'defect_severity_level__defect_classification',
                   'is_fixed', 'fixed_by__username', 'remarks', 'screen_shot')
    except Exception as e:
        s = None
        logger.error(" {0} ".format(str(e)))
    return s


def qa_sheet_header_obj(project, chapter, author, component=None, active_tab=None):

    try:
        # print chapter, "chapter"
        # print active_tab, "active_tab", project, chapter, author
        result = None
        if active_tab and component is not None:
            try:
                chapter_component_obj = ChapterComponent.objects.get(chapter=chapter, component=component)
                result = QASheetHeader.objects.get(project=project, chapter_component=chapter_component_obj,
                                                   author=author,
                                                   review_group=ReviewGroup.objects.get(id=active_tab))
            except Exception as e:
                logger.error(" {0} ".format(str(e)))
                # print "if"
                # print result
        else:
            # print "else"
            result = QASheetHeader.objects.filter(project=project, chapter=chapter, author=author)

    except ObjectDoesNotExist as e:
        # print "except"
        logger.error(" {0} ".format(str(e)))
    return result


def get_review_group():
    return ReviewGroup.objects.all()


def get_template_process_review(request):
    project = request.GET.get('project_id')
    template = request.GET.get('template_id')
    qms_process_model = request.GET.get('qms_process_model')
    chapter = request.GET.get('chapter')
    author = request.GET.get('author')
    tabs = {}
    tab_name = {}
    team_members = {}
    user_tab = {}
    tab_order = {}
    try:

        obj = TemplateProcessReview.objects.filter(template=template, qms_process_model=qms_process_model). \
            order_by('id')
        # print obj
        members_obj = ProjectTeamMember.objects.filter(project=project, member__is_active=True)
        qa_obj = qa_sheet_header_obj(project, chapter, author=author)
        # print "count" ,qa_obj.count()
        for members in members_obj:
            if int(members.member_id) != int(author):
                team_members[int(members.member_id)] = str(members.member.username)

        for ele in obj:
            # print ele.review_group
            tabs[str(ele.review_group)] = bool(ele.is_mandatory)
            tab_name[str(ele.review_group)] = int(ele.review_group.id)
            if qa_obj.count() > 0:
                try:
                    tab_user = qa_obj.get(review_group=ele.review_group)
                except ObjectDoesNotExist:
                    tab_user = None
                if tab_user is not None:
                    user_tab[str(ele.review_group)] = int(tab_user.reviewed_by.id)
                    tab_order[str(ele.review_group)] = int(tab_user.order_number)
                else:
                    user_tab[str(ele.review_group)] = None
                    tab_order[str(ele.review_group)] = None

    except ObjectDoesNotExist:
        tabs = team_members = tab_name = ''
    context_data = {'tabs': tabs, 'tab_name': tab_name, 'team_members': team_members, 'user_tab': user_tab,
                    'tab_order': tab_order}
    # print context_data
    return HttpResponse(
        json.dumps(context_data),
        content_type="application/json"
    )


class AssessmentView(TemplateView):
    template_name = "ansrS_QA_Tmplt_Assessment (Non Platform) QA sheet_3.3.html"

    def get_context_data(self, **kwargs):
        context = super(AssessmentView, self).get_context_data(**kwargs)
        # print "user", self.request.user
        form = BaseAssessmentTemplateForm()
        context['form'] = form
        context['review_group'] = get_review_group()

        return context

    def post(self, request):
        form = BaseAssessmentTemplateForm(request.POST)
        # print request.POST
        # reports = template_id = None
        active_tab = request.session['active_tab'] = request.POST.get('active_tab')
        if form.is_valid():

            project = form.cleaned_data['project']
            chapter = form.cleaned_data['chapter']
            author = form.cleaned_data['author']
            component = form.cleaned_data['component']
            try:

                # print "im in try"
                # print project, chapter, author, active_tab
                request.session['project'] = project
                request.session['chapter'] = chapter
                request.session['author'] = author
                request.session['component'] = component
                obj = qa_sheet_header_obj(project, chapter, author, component, active_tab)
                if obj is None:
                    messages.error(self.request, "Sorry configuration is missing please contact your manager")
                    return render(self.request, self.template_name, {'form': form})
                if request.user == author:
                    request.session['author_logged_in'] = True
                    if not obj.review_group_status:
                        messages.error(self.request, "Sorry You cant access this chapter till review is completed")
                        return render(self.request, self.template_name, {'form': form})
                else:
                    request.session['author_logged_in'] = False
                # print "im here"
                # if obj is None:
                #     messages.error(self.request, "Sorry No Records Found")
                #     return HttpResponseRedirect(reverse('qms'))

                project_template_process_model_obj = ProjectTemplateProcessModel.objects.get(project=project)
                template_id = request.session['template_id'] = project_template_process_model_obj.template.id
                request.session['QA_sheet_header_id'] = obj.id
                defect_master = DefectTypeMaster.objects.all()
                try:
                    reports = get_review(obj)
                    # print reports
                    # request.session['reports'] = list(reports)

                except reports.ObjectDoesNotExist as e:
                    logger.error(" {0} ".format(str(e)))
                    reports = None
                    request.session['template_id'] = template_id = None

            except ObjectDoesNotExist:
                messages.error(self.request, "Sorry No Records Found")
        else:
            form = BaseAssessmentTemplateForm()
        qms_form = review_report_base(template_id, project)

        qms_data = {}
        qms_data_list = []
        severity_count = {}
        if reports and len(reports) != 0:
            # print"im in"
            for eachData in reports:
                # print eachData
                # count = 0
                for k, v in eachData.iteritems():
                    qms_data[k] = v
                    if k == 'id':
                        r_obj = ReviewReport.objects.get(id=int(v))
                        if r_obj.screen_shot:
                            qms_data['screen_shot_url'] = r_obj.screen_shot.url
                            # print r_obj.screen_shot.path
                        else:
                            qms_data['screen_shot_url'] = None
                        qms_data['qms_id'] = v
                    if k == 'review_item':
                        qms_data['review_item'] = v

                    if k == 'defect':
                        qms_data['defect'] = v

                    if k == 'defect_severity_level__severity_type':
                        qms_data['severity_type'] = v

                    if k == 'defect_severity_level__severity_level':
                        qms_data['severity_level'] = v
                        if v in severity_count:
                            v = int(v)
                            severity_count[v] += 1
                        else:
                            severity_count[v] = 1
                            # print count, severity_count, v

                    if k == 'defect_severity_level__defect_classification':
                        qms_data['defect_classification'] = v

                    if k == 'is_fixed':
                        qms_data['is_fixed'] = v

                    if k == 'screen_shot':
                        # url = ReviewReport.objects.get(id=obj.id)
                        qms_data['screen_shot'] = v
                        # if v:
                        #     qms_data['screen_shot_url'] = v

                    if k == 'fixed_by__username':
                        qms_data['fixed_by'] = v

                    if k == 'remarks':
                        qms_data['remarks'] = v
                    # qms_data['clear_screen_shot'] = False
                # print qms_data
                qms_data_list.append(qms_data.copy())

            qms_data.clear()
        # print qms_data_list
        qms_formset = formset_factory(
            qms_form, max_num=1, can_delete=True
        )

        qms_formset = qms_formset(initial=qms_data_list)
        score = {}
        tmp_weight = {}
        defect_density = {}
        # print severity_count
        s = SeverityLevelMaster.objects.filter(is_active=True)
        for k, v in severity_count.iteritems():
            severity_level_obj = s.get(id=int(k))
            tmp_weight[k] = float(severity_level_obj.penalty_count) * v
            score[k] = 100 - (tmp_weight[k])
            if obj.count > 0:
                defect_density[k] = (tmp_weight[k] / obj.count) * 100
            else:
                defect_density[k] = 0

        total_count = sum(severity_count.itervalues())
        weight = sum(tmp_weight.itervalues())
        if weight != 0:
            total_score = 100 - sum(tmp_weight.itervalues())
        else:
            total_score = 0
        total_defect_density = sum(defect_density.itervalues())
        return render(self.request, self.template_name, {'form': form, 'defect_master': DefectTypeMaster.objects.all(),
                                                         'reports': reports, 'review_formset': qms_formset,
                                                         'template_id': template_id,
                                                         'review_group': get_review_group(), 'questions': obj.count,
                                                         'severity_count': severity_count,
                                                         'score': score, 'total_score': total_score,
                                                         'total_count': total_count, 'defect_density': defect_density,
                                                         'total_defect_density': total_defect_density,
                                                         'severity_level':
                                                             SeverityLevelMaster.objects.filter(is_active=True)
                      .values_list('name', 'id', )})

# def qms_data(reports):
#     qms_data = {}
#     qms_data_list = []
#     severity_count = {}
#     if reports and len(reports) != 0:
#         # print"im in"
#         for eachData in reports:
#             # print eachData
#             # count = 0
#             for k, v in eachData.iteritems():
#                 qms_data[k] = v
#                 if k == 'id':
#                     r_obj = ReviewReport.objects.get(id=int(v))
#                     if r_obj.screen_shot:
#                         qms_data['screen_shot_url'] = r_obj.screen_shot.url
#                         print r_obj.screen_shot.path
#                     else:
#                         qms_data['screen_shot_url'] = None
#                     qms_data['qms_id'] = v
#                 if k == 'review_item':
#                     qms_data['review_item'] = v
#
#                 if k == 'defect':
#                     qms_data['defect'] = v
#
#                 if k == 'defect_severity_level__severity_type':
#                     qms_data['severity_type'] = v
#
#                 if k == 'defect_severity_level__severity_level':
#                     qms_data['severity_level'] = v
#                     if v in severity_count:
#                         v = int(v)
#                         severity_count[v] += 1
#                     else:
#                         severity_count[v] = 1
#                         # print count, severity_count, v
#
#                 if k == 'defect_severity_level__defect_classification':
#                     qms_data['defect_classification'] = v
#
#                 if k == 'is_fixed':
#                     qms_data['is_fixed'] = v
#
#                 if k == 'screen_shot':
#                     # url = ReviewReport.objects.get(id=obj.id)
#                     qms_data['screen_shot'] = v
#                     # if v:
#                     #     qms_data['screen_shot_url'] = v
#
#                 if k == 'fixed_by__username':
#                     qms_data['fixed_by'] = v
#
#                 if k == 'remarks':
#                     qms_data['remarks'] = v
#                     # qms_data['clear_screen_shot'] = False
#             # print qms_data
#             qms_data_list.append(qms_data.copy())
#
#         qms_data.clear()
#     print qms_data_list
#     qms_formset = formset_factory(
#         qms_form, max_num=1, can_delete=True
#     )
#
#     qms_formset = qms_formset(initial=qms_data_list)
#     score = {}
#     tmp_weight = {}
#     defect_density = {}
#     # print severity_count
#     s = SeverityLevelMaster.objects.filter(is_active=True)
#     for k, v in severity_count.iteritems():
#         severity_level_obj = s.get(id=int(k))
#         tmp_weight[k] = float(severity_level_obj.penalty_count) * v
#         score[k] = 100 - (tmp_weight[k])
#         if obj.count > 0:
#             defect_density[k] = (tmp_weight[k] / obj.count) * 100
#         else:
#             defect_density[k] = 0
#
#     total_count = sum(severity_count.itervalues())
#     weight = sum(tmp_weight.itervalues())
#     if weight != 0:
#         total_score = 100 - sum(tmp_weight.itervalues())
#     else:
#         total_score = 0
#     total_defect_density = sum(defect_density.itervalues())
#     return render(self.request, self.template_name, {'form': form, 'defect_master': DefectTypeMaster.objects.all(),
#                                                      'reports': reports, 'review_formset': qms_formset,
#                                                      'template_id': template_id,
#                                                      'review_group': get_review_group(), 'questions': obj.count,
#                                                      'severity_count': severity_count,
#                                                      'score': score, 'total_score': total_score,
#                                                      'total_count': total_count, 'defect_density': defect_density,
#                                                      'total_defect_density': total_defect_density,
#                                                      'severity_level':
#                                                          SeverityLevelMaster.objects.filter(is_active=True)
#                   .values_list('name', 'id', )})

class ReviewReportManipulationView(AssessmentView):

    def post(self, request):
        # print request.POST
        # print request.FILES
        # print "im in formset post"
        fail = 0
        qms_data = {}
        qms_data_list = []
        request.session['active_tab'] = active_tab = request.POST.get('active_tab1')
        # print request.POST.get('active_tab1')
        qms_form = review_report_base(request.session['template_id'], request.session['project'])
        qms_formset = formset_factory(
            qms_form,  max_num=1, can_delete=True
        )

        AllowedFileTypes = ['jpg', 'png', 'pdf', 'xlsx', 'xls', 'docx', 'doc', 'jpeg', 'eml', 'zip', 'gz', '7z']


        forbidden_file_type = False

        q_form = qms_formset(request.POST, request.FILES)
        if q_form.is_valid():

            for form_elements in q_form:
                # print form_elements
                if form_elements.cleaned_data['DELETE'] is True:
                    # form_elements.cleaned_data['DELETE']
                    ReviewReport.objects.filter(id=form_elements.cleaned_data['qms_id']).update(is_active=False)
                else:
                    del(form_elements.cleaned_data['DELETE'])
                    for k, v in form_elements.cleaned_data.iteritems():
                        qms_data[k] = v
                    qms_data_list.append(qms_data.copy())
                    qms_data.clear()
                    # print qms_data_list
            for obj in qms_data_list:
                print obj
                if obj['qms_id'] > 0:
                    report = ReviewReport.objects.get(id=obj['qms_id'])
                    # print obj['qms_id']
                else:
                    # print obj['qms_id']
                    report = ReviewReport()
                    report.created_by = request.user
                if not request.session['author_logged_in']:
                    report.review_item = obj['review_item']
                    report.defect = obj['defect']
                    #  below is backend check preventing author from changing severity type
                    # obj['severity_type'] = report.defect_severity_level.severity_type
                if obj['screen_shot']:
                    # extension = os.path.splitext(obj['screen_shot'])[1]


                    # if request.FILES['admin_action_attachment'].name.split(".")[-1] not in AllowedFileTypes:
                    if obj['screen_shot'].name.split(".")[-1] not in AllowedFileTypes:

                        messages.error(request, "You can't upload this file type")


                        forbidden_file_type = True

                    else:
                        report.screen_shot = obj['screen_shot']
                # if obj['clear_screen_shot']:
                #     report.screen_shot = None
                report.is_fixed = obj['is_fixed']
                report.remarks = obj['remarks']
                if len(obj['remarks']) > 0:
                    report.fixed_by = request.user
                # print request.session['template_id']
                #
                # print request.session['active_tab']
                # print obj['severity_type']
                # import ipdb
                # ipdb.set_trace()

                # import ipdb
                # ipdb.set_trace()

                try:
                    # 1
                    # Grammar and style
                    # 2

                    # print request.session['template_id'], obj['severity_type'] , active_tab
                    review_group = ReviewGroup.objects.get(id=active_tab)
                    defect_obj = DefectSeverityLevel.objects.filter(template_id=request.session['template_id'],
                                                                    severity_type=obj['severity_type'],
                                                                    review_master=review_group.review_master)[0]

                    report.defect_severity_level = defect_obj
                    # report.defect_severity_level = DefectSeverityLevel.objects.get(id=defect_obj.id)
                    qa_obj = QASheetHeader.objects.get(id=request.session['QA_sheet_header_id'])
                    report.QA_sheet_header = qa_obj
                    report.updated_by = request.user
                    report.save()
                    try:
                        qa_obj.count = int(request.POST.get('questions'))
                        qa_obj.save()
                    except Exception as e:
                        logger.error(" {0} ".format(str(e)))

                except DefectSeverityLevel.DoesNotExist as e:
                    logger.error(" {0} ".format(str(e)))
                    fail += 1

        else:
            # print q_form.errors
            messages.error(request, q_form.errors)
            # context = {'form': BaseAssessmentTemplateForm(), 'review_formset': qms_formset}
        if fail == 0:
            if forbidden_file_type:
                messages.error(request, "You can't upload this file type but your data is saved")
            else:
                messages.info(request, "successfully saved")
        else:
            messages.error(request, "Configuration is Missing")

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
    review_group = ReviewGroup.objects.get(id=request.GET.get('active_tab'))
    try:
        obj = DefectSeverityLevel.objects.filter(template=template_id, severity_type=severity,
                                                 review_master=review_group.review_master)[0]
        # logger.error("query {0} ".format(obj.query))
        context_data = {'severity_level': str(obj.severity_level), 'defect_classification': str(obj.defect_classification)}
    except IndexError as e:
        logger.error("query {0} ".format(str(e)))
        context_data = {'configuration_missing': True}

    return HttpResponse(
            json.dumps(context_data),
            content_type="application/json"
        )


def fetch_members(project):
    user = ProjectTeamMember.objects.filter(project=project, member__is_active=True)
    qs = User.objects.filter(pk__in=user)
    return user


def fetch_author(request):
    project_id = request.GET.get('project_id')
    chapter_id = request.GET.get('chapter_id')
    component_id = request.GET.get('component_id')

    try:
        chapter_component = ChapterComponent.objects.get(chapter=chapter_id, component=component_id)
        author = QASheetHeader.objects.filter(project_id=project_id,
                                              chapter_component=chapter_component).values_list('author', flat=True)[0]
    except Exception as e:
        author = None
    # obj = User.objects.get(pk=user)
    team_members = {}
    team = fetch_members(project_id)
    for members in team:
        team_members[int(members.member_id)] = str(members.member.username)
    context_data = {'author': str(author), 'team_members': team_members}
    # print context_data
    return HttpResponse(
        json.dumps(context_data),
        content_type="application/json"
    )


# def check_permission(request):
#     project_id = request.GET.get('project_id')
#     active_tab = request.GET.get('active_tab')
#
#     try:
#         result = QASheetHeader.objects.filter(project_id=project_id, review_group_id=active_tab).\
#             values_list('review_group_status', flat=True)[0]
#     except Exception as e:
#         result = False
#         logger.error(" check permission for author failed {0} ".format(str(e)))
#     return HttpResponse(
#         json.dumps(bool(result)),
#         content_type="application/json"
#     )

class DashboardView(ListView):
    model = ReviewReport
    template_name = 'qms_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        # print "user", self.request.user

        # s = ReviewReport.objects.filter(QA_sheet_header__project__ProjectDetail__deliveryManager=self.request.user). \
        context['projects'] = ProjectTemplateProcessModel.objects.filter(project__in=ProjectManager.objects.
                                                                         filter(user=self.request.user).
                                                                         values('project')).\
            values('id', 'project', 'project__projectId', 'project__name').\
            annotate(chapter_count=Count('project__book__chapter'))
        # print context['projects']

        return context



























     # values('QA_sheet_header__project__name', 'QA_sheet_header__project__customer').annotate(Count('QA_sheet_header__project__customer'))
        # customers =  ProjectManager.objects.filter(user=self.request.user).values('project__customer__name')
        # print customers
        # cust_data = {}
        # cust_list = []
        # tmp = {}
        # for d in customers:
        #    tmp[d.name] =
        #     for k,v in d.iteritems():
        #         if k is 'project__customer__name':
        #             cust_data[k] = {}
        #
        #         cust_list.append(cust_data.copy())
        #     cust_data.clear()
        # import json
        # print json.dumps(cust_list)
        # print "dict",tmp
        #
        #
        # for k, v in customers.iteritems():
        #     cust_data[k] = v
        #     cust_list.append(cust_data.copy())
        # cust_data.clear()
        # print cust_list
        # [{'project': 886L, 'project__customer': 19L}, {'project': 942L, 'project__customer': 19L},
        #  {'project': 944L, 'project__customer': 19L}, {'project': 1071L, 'project__customer': 19L},
        #  {'project': 757L, 'project__customer': 19L}, {'project': 1085L, 'project__customer': 19L},
        #  {'project': 1121L, 'project__customer': 19L}, {'project': 1249L, 'project__customer': 19L},
        #  {'project': 1487L, 'project__customer': 19L}, {'project': 1830L, 'project__customer': 19L},
        #  {'project': 1960L, 'project__customer': 19L}]

        # s=  Project.objects.filter(
        #         #closed=False,
        #         endDate__gte=enddate,
        #         #endDate__gte=datetime.date.today(),
        #         id__in=ProjectTeamMember.objects.filter(
        #             Q(member=self.request.user) |
        #             Q(project__projectManager=self.request.user)
        #         ).values('project_id')
        #     ).order_by('customer_id')
        # (1L, 1960L, datetime.date(2017, 3, 31), 2, 2)
        # (2L, 1960L, datetime.date(2017, 3, 31), 1, 1)
        # s = {}
        # tmp = {}
        # print s
        # for k in s:
        #     for key,value in  k.iteritems():
        #         if key is 'QA_sheet_header__project__name':
        #             tmp[value] =
            # if 'QA_sheet_header__project' in s:
            #     print True
            # else : print False
        #     print k['QA_sheet_header__project__endDate']  # values(
        # 'defect_severity_level', 'QA_sheet_header__project', 'QA_sheet_header__project__endDate').\
        # print s.query

        # [{'defect_severity_level': 1L, 'QA_sheet_header__project__count': 2, 'defect_severity_level__count': 2,
        #   'QA_sheet_header__project__endDate': datetime.date(2017, 3, 31), 'QA_sheet_header__project': 1960L},
        #  {'defect_severity_level': 2L, 'QA_sheet_header__project__count': 1, 'defect_severity_level__count': 1,
        #   'QA_sheet_header__project__endDate': datetime.date(2017, 3, 31), 'QA_sheet_header__project': 1960L},
        #  {'defect_severity_level': 1L, 'QA_sheet_header__project__count': 1, 'defect_severity_level__count': 1,
        #   'QA_sheet_header__project__endDate': datetime.date(2016, 12, 31), 'QA_sheet_header__project': 1487L},
        #  {'defect_severity_level': 2L, 'QA_sheet_header__project__count': 1, 'defect_severity_level__count': 1,
        #   'QA_sheet_header__project__endDate': datetime.date(2016, 12, 31), 'QA_sheet_header__project': 1487L}]

        # # form = BaseAssessmentTemplateForm()
        # # context['form'] = form
        # context['review_group'] = get_review_group()
        # context