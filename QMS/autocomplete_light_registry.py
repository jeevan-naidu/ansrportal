from django.contrib.auth.models import User
from django.db.models import Q
from MyANSRSource.models import ProjectTeamMember, ProjectManager, ProjectDetail
from .models import *
from dal import autocomplete
import datetime


class AutocompleteUser(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = User.objects.filter(
            Q(is_superuser=False) & Q(is_active=True)
        )
        choices = choices.filter(email__icontains=q)
        return choices


class AutocompleteProjectsManager(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = ProjectDetail.objects.filter(Q(deliveryManager=self.request.user) | Q(pmDelegate=self.request.user),
                                               project__endDate__gte=datetime.date.today())\
            .exclude(id__in=ProjectTemplateProcessModel.objects.filter(lead_review_status=True)).values('project')

        # choices = Project.objects.filter(id__in=ProjectManager.objects.filter(user=self.request.user).
        # values('project')
        #                                  , endDate__gte=datetime.date.today())

        choices = choices.filter(name__icontains=q)
        return choices


# qms_project , project_detail_project are  related_name
class AutocompleteDMProjects(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        q = self.request.GET.get('q', '')

        choices = Project.objects.filter(Q(project_detail_project__deliveryManager=self.request.user) |
                                         Q(project_detail_project__pmDelegate=self.request.user),
                                         endDate__gte=datetime.date.today(), closed=False,  active=True).exclude(
                                         qms_project__lead_review_status=True).order_by('name').distinct()
        choices = choices.filter(name__icontains=q)
        return choices


class AutocompleteProject(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = Project.objects.filter(Q(project_detail_project__deliveryManager=self.request.user) |
                                         Q(project_detail_project__pmDelegate=self.request.user) |
                                         Q(project_team_member_project__member=self.request.user),
                                         endDate__gte=datetime.date.today(), closed=False,  active=True,
                                         qms_project__lead_review_status=False).order_by('name').distinct()
        choices = choices.filter(name__icontains=q)
        return choices


class AutocompleteTemplates(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        project = self.forwarded.get('project', None)
        qms_process_model = self.forwarded.get('qms_process_model', None)
        try:
            # print "im in try"
            obj = ProjectTemplateProcessModel.objects.get(project=project, qms_process_model=qms_process_model)
            # print obj
            choices = TemplateMaster.objects.filter(id=obj.template_id)
        except:
            # print "excep"
            try:
                choices = TemplateProcessReview.objects.filter(qms_process_model=qms_process_model).values_list('template_id',flat=True)

                choices = TemplateMaster.objects.filter(id__in=choices)
            except:
                choices = TemplateMaster.objects.filter(name__icontains=q)
            # print choices

        return choices


class AutocompleteProcessModel(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        project = self.forwarded.get('project', None)
        try:
            obj = ProjectTemplateProcessModel.objects.get(project=project)
            choices = QMSProcessModel.objects.filter(id=obj.qms_process_model_id)

        except:
            # print "im in except"
            choices = QMSProcessModel.objects.filter(name__icontains=q)
        return choices


class AutocompleteReviewGroup(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = ReviewGroup.objects.filter(name__icontains=q)
        return choices


class AutocompleteChapters(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = Chapter.objects.all()

        project = self.forwarded.get('project', None)
        try:
            project_obj = Project.objects.get(id=int(project))
        except:
            project_obj = None

        if project:
            qs = qs.filter(book=project_obj.book)

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class AutocompleteComponents(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = ComponentMaster.objects.filter(name__icontains=q)
        return choices


# for second screen in qms
class AutoCompleteUserProjectSpecific(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = User.objects.all()

        project = self.forwarded.get('project', None)
        # print project
        chapter = self.forwarded.get('chapter', None)
        component = self.forwarded.get('component', None)

        # print project ,chapter ,component
        try:
            user = QASheetHeader.objects.filter \
                (project=project, chapter_component=ChapterComponent.objects.
                 get(chapter=chapter, component=component)).values_list('author', flat=True).first()
            # print user
            qs = qs.filter(pk=user)

        except:
            qs = None
        #
        # if self.q:
        #     qs = qs.filter(pk=user)

        return qs


# for first screen in qms
class AutoCompleteAssignUserProjectSpecific(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        # qs = User.objects.all()

        project = self.forwarded.get('project', None)

        try:
            # print project

            user = ProjectTeamMember.objects.filter(project=project, member__is_active=True).values_list('member_id')
            # print user
            try:
                qs = User.objects.filter(pk__in=user)
            except Exception, e:
                pass
                # print "AutoCompleteAssignUserProjectSpecific" , str(e)
                # # for i in user:
                # #     print i.member_id
                #
                # # qs = qs.filter(pk=user.member_id)

        except:
            qs = None
        #
        # if self.q:
        #     qs = qs.filter(pk=user)

        return qs


class AutoCompleteChapterSpecificComponent(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        project = self.forwarded.get('project', None)
        chapter = self.forwarded.get('chapter', None)
        try:
            obj = QASheetHeader.objects.filter(project=project, chapter=chapter).values_list("chapter_component_id",
                                                                                             flat=True).distinct()
            # print obj
            component = ChapterComponent.objects.filter(id__in=obj).values("component")
            component = ComponentMaster.objects.filter(id__in=component)
        except Exception as e:
            # print str(e)
            component = None

        return component