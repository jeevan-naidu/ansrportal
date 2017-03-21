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
            # print v
            if v:
                v = int(v)
            if v and v != 0:
                order_number[order_id[1]] = v
            else:
                # print 'else'
                messages.error(self.request, 'Order Number Cannot Be 0')
                return super(ChooseTabs, self).form_valid(form)

        # {u'user_3': u'256', u'user_1': u'255'}
        # print users
        # print order

        try:
            ProjectTemplateProcessModel.objects.get_or_create(template=form.cleaned_data['template'],
                                                              project=form.cleaned_data['project'],
                                                              qms_process_model=form.cleaned_data['qms_process_model'],
                                                              created_by=self.request.user)
        except Exception as e:
            # print "ChooseTabs", (str(e))
            logger.error(" {0} ".format(str(e)))

        cm_obj, chapter_component = ChapterComponent.objects.get_or_create(chapter=form.cleaned_data['chapter'],
                                                                           component=form.cleaned_data['component'],
                                                                           created_by=self.request.user, )
        # print form.cleaned_data['chapter'] , form.cleaned_data['component']
        # print"res", cm_obj
        # print "obj", chapter_component
        # print user_tab
        for k, v in user_tab.iteritems():
            # print form.cleaned_data['author']
            # k = int(k)
            # print k, order_number[k]
            obj, created = QASheetHeader.objects.update_or_create(project=form.cleaned_data['project'],
                                                                  chapter=form.cleaned_data['chapter'],
                                                                  chapter_component=cm_obj,
                                                                  review_group_id=int(k),
                                                                  defaults={'author': form.cleaned_data['author'],
                                                                            'reviewed_by_id': int(v),
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
                   'is_fixed', 'fixed_by__username', 'remarks', 'screen_shot', 'instruction')
    except Exception as e:
        s = None
        logger.error(" {0} ".format(str(e)))
    return s


def qa_sheet_header_obj(project, chapter, author, component=None, active_tab=None):

    try:
        # print chapter, "chapter"
        # print active_tab, "-<active_tab->", project.id, chapter, author
        result = None
        if active_tab and component is not None:
            if active_tab == 'lambda':
                review_obj = ReviewGroup.objects.order_by('id').first()
            else:
                review_obj = ReviewGroup.objects.get(id=active_tab)
            try:
                # print "im in try"
                chapter_component_obj = ChapterComponent.objects.get(chapter=chapter, component=component)
                # print chapter_component_obj.id
                result = QASheetHeader.objects.get(project=project, chapter_component=chapter_component_obj,
                                                   author=author,
                                                   review_group=review_obj)
                # print result
            except Exception as e:
                # print "qa_sheet_header_obj" , str(e)
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


def get_review_group(project=None, chapter=None, is_author=False):
    # print "get_review_group"
    obj = ReviewGroup.objects.all()
    # print is_author , project,chapter

    try:
        if not is_author and project and chapter:
            obj = obj.filter(pk__in=QASheetHeader.objects.filter(project=project, chapter=chapter).
                             values_list('review_group_id', flat=True).order_by('order_number'))
            # print obj
    except Exception as e:
        pass
        # print "get_review_group" , str(e)
    return obj


def get_template_process_review(request):
    # print request.GET
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
    can_edit = {}
    config_missing = False
    try:

        obj = TemplateProcessReview.objects.filter(template=template, qms_process_model=qms_process_model). \
            order_by('id')
        if not obj:
            config_missing = True
        members_obj = ProjectTeamMember.objects.filter(project=project, member__is_active=True)
        qa_obj = qa_sheet_header_obj(project, chapter, author=author)
        # print "qa_obj" ,qa_obj
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
                    review_report_obj = ReviewReport.objects.filter(QA_sheet_header__project=project,
                                                                    QA_sheet_header__review_group=ele.review_group)
                    if review_report_obj:
                        can_edit[str(ele.review_group.id)] = False
                    else:
                        can_edit[str(ele.review_group.id)] = True
                except ObjectDoesNotExist:
                    tab_user = None
                if tab_user is not None:
                    user_tab[str(ele.review_group)] = int(tab_user.reviewed_by.id)
                    tab_order[str(ele.review_group)] = int(tab_user.order_number)
                else:
                    user_tab[str(ele.review_group)] = None
                    tab_order[str(ele.review_group)] = None

    except ObjectDoesNotExist:
        tabs, team_members, tab_name = ''
    context_data = {'tabs': tabs, 'tab_name': tab_name, 'team_members': team_members, 'user_tab': user_tab,
                    'tab_order': tab_order, 'config_missing': config_missing, "can_edit": can_edit}
    # print context_data
    return HttpResponse(
        json.dumps(context_data),
        content_type="application/json"
    )


def forbidden_access(self, form, project, message_code, chapter=None):
    msg_dict = {'not_assigned': "Sorry You are not assigned to  this chapter",
                "config_missing": "Sorry configuration is missing please contact your manager",
                "wait": "Sorry You cant access this chapter till review is completed",
                "config_missing_manager": "Hey you didn't configure for this review please do it",
                }

    messages.error(self.request, msg_dict[message_code])
    return render(self.request, self.template_name, {'form': form,
                                                     'review_group': get_review_group(project, chapter), })


class AssessmentView(TemplateView):
    template_name = "ansrS_QA_Tmplt_Assessment (Non Platform) QA sheet_3.3.html"

    def get_context_data(self, **kwargs):
        context = super(AssessmentView, self).get_context_data(**kwargs)
        # print "user", self.request.user
        form = BaseAssessmentTemplateForm()
        context['form'] = form
        # context['review_group'] = get_review_group()

        return context

    def post(self, request):
        form = BaseAssessmentTemplateForm(request.POST)
        # for sa in request.POST :
        # print request.POST
        # reports = template_id = None
        active_tab = request.POST.get('active_tab')
        request.session['active_tab'] = request.POST.get('active_tab')
        # print "after ass " , active_tab
        # print request.POST
        if form.is_valid():

            project = form.cleaned_data['project']
            chapter = form.cleaned_data['chapter']
            author = form.cleaned_data['author']
            component = form.cleaned_data['component']

            if request.user is author:
                # print"is author"
                get_review_group(project, chapter, is_author=False)
            try:

                # print "im in try"
                # print project.id, chapter, author, active_tab

                request.session['project'] = project
                request.session['chapter'] = chapter
                request.session['author'] = author
                request.session['component'] = component
                obj = qa_sheet_header_obj(project, chapter, author, component, active_tab)
                # print "status", obj.author_feedback_status

                is_pm = ProjectManager.objects.filter(project=project, user=request.user).exists()
                # print is_pm, request.user, author
                if obj is None:
                    if is_pm:
                        msg = "config_missing_manager"
                    else:
                        msg = "config_missing"
                    return forbidden_access(self, form, project, msg, chapter)
                else:
                    qms_team_members = [obj.reviewed_by, author]
                    if request.user == author:
                        request.session['author_logged_in'] = True
                        if not obj.review_group_status and not obj.author_feedback_status:
                            return forbidden_access(self, form, project, "wait",chapter)
                    else:
                        # print request.user , author
                        request.session['author_logged_in'] = False

                    if not is_pm and request.user not in qms_team_members:
                        return forbidden_access(self, form, project, "not_assigned",chapter)

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
        qms_form = review_report_base(template_id, project, ChapterComponent.objects.get(chapter=chapter,
                                                                                         component=component) ,
                                      request_obj=self.request, tab=obj.review_group_id)

        qms_data = {}
        qms_data_list = []
        severity_count = {}
        if reports and len(reports) != 0:
            # print"im in"
            for eachData in reports:
                # print "ed", eachData
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

                    if k == 'instruction':
                        qms_data['instruction'] = v

                    if k == 'defect_severity_level__severity_type':
                        qms_data['severity_type'] = v

                    if k == 'defect_severity_level__severity_level':
                        qms_data['severity_level'] = v
                        if v in severity_count:
                            v = int(v)
                            severity_count[v] += 1
                        else:
                            severity_count[v] = 1
                            # print severity_count, v

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
                # print "" qms_data
                qms_data_list.append(qms_data.copy())

            qms_data.clear()
        # print "qms_data_list" , qms_data_list
        qms_formset = formset_factory(
            qms_form, max_num=1, can_delete=True
        )
        if len(qms_data_list):
            qms_formset = qms_formset(initial=qms_data_list)
        else:
            qms_formset = formset_factory(
                qms_form, extra =1 , max_num=1, can_delete=True
            )
        # qms_formset = formset_factory(
        #     qms_form, max_num=1, can_delete=True
        # )
        score = {}
        tmp_weight = {}
        defect_density = {}
        # print severity_count
        s = SeverityLevelMaster.objects.filter(is_active=True).exclude(name__icontains='S0')
        for k, v in severity_count.iteritems():
            severity_level_obj = s.get(id=int(k))
            tmp_weight[k] = float(severity_level_obj.penalty_count) * v
            score[k] = 100 - (tmp_weight[k])
            if obj.count > 0:
                defect_density[k] = round(((tmp_weight[k] / obj.count) * 100), 2)
            else:
                defect_density[k] = 0

        total_count = sum(severity_count.itervalues())
        weight = sum(tmp_weight.itervalues())
        if weight != 0:
            total_score = 100 - sum(tmp_weight.itervalues())
        else:
            total_score = 0
        total_defect_density = sum(defect_density.itervalues())
        severity_level_obj = SeverityLevelMaster.objects.filter(is_active=True).values_list('name', 'id').\
            exclude(name__icontains='S0')

        return render(self.request, self.template_name, {'form': form, 'defect_master': DefectTypeMaster.objects.all(),
                                                         'reports': reports, 'review_formset': qms_formset,
                                                         "author_feedback_status": obj.author_feedback_status,
                                                         "reviewer_feedback_status": obj.review_group_status,
                                                         'template_id': template_id,
                                                         'review_group': get_review_group(project, chapter),
                                                         'questions': obj.count,
                                                         'severity_count': severity_count, 'project': project.id,
                                                         'score': score, 'total_score': total_score,
                                                         'total_count': total_count, 'defect_density': defect_density,
                                                         'total_defect_density': total_defect_density,
                                                         'severity_level': severity_level_obj})


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
        qms_form = review_report_base(request.session['template_id'], request.session['project'],
                                      request_obj=self.request ,tab =active_tab )
        qms_formset = formset_factory(
            qms_form,  max_num=1, can_delete=True
        )
        AllowedFileTypes = ['jpg', 'png', 'pdf', 'xlsx', 'xls', 'docx', 'doc', 'jpeg', 'eml', 'zip', 'gz', '7z']

        forbidden_file_type = False

        q_form = qms_formset(request.POST, request.FILES)
        # print request.POST
        # print q_form.is_valid()
        # print q_form.errors
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
                # print obj
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
                    # review_group = ReviewGroup.objects.get(id=active_tab)
                    defect_obj = DefectSeverityLevel.objects.filter(
                                                                    severity_type=obj['severity_type'],
                                                                    )[0]

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
    # print request.GET
    template_id = request.GET.get('template_id')
    project_id = request.GET.get('project_id')
    severity = request.GET.get('severity_type')
    request.session['active_tab'] = request.GET.get('active_tab')
    review_group = ReviewGroup.objects.get(id=request.GET.get('active_tab'))
    severity_classification = request.GET.get('severity_classification')
    # print request.GET
    obj = ProjectTemplateProcessModel.objects.get(template_id=template_id, project_id=project_id)
    if obj.qms_process_model.product_type == 1 :
        media_team = True
    else:
        media_team = False
    if not media_team:
        try:
            # print "severity", severity
            obj = DefectSeverityLevel.objects.filter(severity_type=severity)[0]
            # print "obj" , obj
            # logger.error("query {0} ".format(obj.query))
            context_data = {'severity_level': str(obj.severity_level), 'defect_classification':
                { str(obj.defect_classification): obj.defect_classification.id}}
        except IndexError as e:
            logger.error("query {0} ".format(str(e)))
            context_data = {'configuration_missing': True}

    else:
        if request.GET.get('triggered_by') == 'severity_type':
            # print"im in buddy"
            try:
                s = DefectSeverityLevel.objects.filter(severity_type=severity).values_list("defect_classification__name",
                                                                                           "defect_classification__id")
                classification_dict = dict((str(x), int(y)) for x, y in s)
                classification_dict["fghg"] =5
                context_data = {'classification_dict': classification_dict, "triggered_by": request.GET.get('triggered_by')}

            except:
                context_data = {'configuration_missing': True, "triggered_by": request.GET.get('triggered_by')}
            return HttpResponse(
                json.dumps(context_data),
                content_type="application/json"
            )
        if severity_classification != "None":
            is_media = True
        else:
            is_media = False
        try:
            if is_media:
                obj = DefectSeverityLevel.objects.filter(severity_type=severity,
                                                         defect_classification=severity_classification)[0]

            else:
                obj = DefectSeverityLevel.objects.filter(severity_type=severity)[0]
            # logger.error("query {0} ".format(obj.query))
            context_data = {'severity_level': str(obj.severity_level), 'defect_classification':
                {str(obj.defect_classification): obj.defect_classification.id}, "is_media": is_media}
        except IndexError as e:
            logger.error("query {0} ".format(str(e)))
            context_data = {'configuration_missing': True, "is_media": is_media}
    # print json.dumps(context_data)
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
        # print "fetch_author", str(e)
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
        # s = ReviewReport.objects.filter(QA_sheet_header__project__ProjectDetail__deliveryManager=self.request.user). \
        context['projects'] = ProjectTemplateProcessModel.objects.filter(project__in=ProjectManager.objects.
                                                                         filter(user=self.request.user).
                                                                         values('project')).\
            values('id', 'project', 'project_id', 'project__projectId', 'project__name', 'template_id').\
            annotate(chapter_count=Count('project__book__chapter'))
        print (context['projects'])
        return context


def review_completed(request):
    project_id = request.GET.get('project_id')
    chapter_id = request.GET.get('chapter_id')
    review_feedback = request.GET.get('review_feedback')
    review_group = request.GET.get('review_group')
    submitted_by = request.GET.get('submitted_by')
    status = 0
    try:
        # print project_id,chapter_id,review_group,review_feedback
        if submitted_by == "author":
            QASheetHeader.objects.filter(project_id=project_id, chapter_id=chapter_id,
                                         review_group_id=review_group).update(author_feedback_status=True,
                                                                              author_feedback=review_feedback)
        else:
            QASheetHeader.objects.filter(project_id=project_id, chapter_id=chapter_id,
                                         review_group_id=review_group).update(review_group_status=True,
                                                                              review_group_feedback=review_feedback)
        status = 1
    except Exception as e:
        print str(e)
        logger.error("check permission for author failed {0} ".format(str(e)))

    return HttpResponse(
        json.dumps(status),
        content_type="application/json"
    )


def chapter_summary(request):
    project_id = request.GET.get('project_id')
    review_report_obj = ReviewReport.objects.filter(QA_sheet_header__project_id=project_id).\
        values('QA_sheet_header__chapter_id').distinct()
    qms_data = {}
    qms_data_list = []
    tmp_dict = {}
    severity_level = SeverityLevelMaster.objects.all().exclude(name__icontains='S0')
    if review_report_obj:
        for eachData in review_report_obj:
            for k, v in eachData.iteritems():
                if k is 'QA_sheet_header__chapter_id':
                    obj = Chapter.objects.get(id=v)
                    qms_data[obj.id] = {}
                    qms_data[obj.id]['severity_level'] = {}
                    qms_data[obj.id]['name'] = obj.name
                    tmp_obj = QASheetHeader.objects.filter(project_id=project_id, chapter_id=obj.id)
                    question_count = sum(tmp_obj.filter().values_list('count', flat=True))
                    # print question_count
                    qa_obj = tmp_obj[0]
                    qms_data[obj.id]['author'] = qa_obj.author.username

                    for s in severity_level:
                        # print "s",s
                        s_count = review_report_obj.filter(defect_severity_level__severity_level=s).\
                            values('defect_severity_level__severity_level__name',
                                   'defect_severity_level__severity_level').\
                            annotate(s_count=Count('defect_severity_level__severity_level'))
                        if not s_count:
                            qms_data[obj.id]['severity_level'][s.name] = 0
                            tmp_dict[s.name] = 0
                        else:
                            for c in s_count:
                                try:
                                    qms_data[obj.id]['severity_level'][s.name] = c['s_count']
                                    tmp_dict[s.name] = (c['s_count'] * s.penalty_count) / question_count
                                except Exception as e:
                                    print str(e)
                                    logger.error(" qms {0} ".format(str(e)))
                        # print tmp_dict
                        tmp_dd = float(sum(tmp_dict.values()) * 100)
                        qms_data[obj.id]['defect_density'] = str(round(tmp_dd, 2))
                        qms_data[obj.id]['questions'] = question_count
                        # qms_data[obj.id]['severity_level'] = tmp_dict
            qms_data_list.append(qms_data.copy())
            qms_data.clear()
    print (qms_data_list)
    return HttpResponse(
        json.dumps(qms_data_list),
        content_type="application/json"
    )

