from django.contrib.auth.models import User
from django.db.models import Q
from MyANSRSource.models import ProjectTeamMember, ProjectManager
from .models import *
from dal import autocomplete


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
        choices = Project.objects.filter(
            id__in=ProjectManager.objects.filter(
                user=self.request.user
            ).values('project')
        )
        choices = choices.filter(name__icontains=q)
        return choices


class AutocompleteProjects(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = Project.objects.filter(
            closed=False,
            id__in=ProjectTeamMember.objects.filter(
                Q(member=self.request.user) |
                Q(project__projectManager=self.request.user)
            ).values('project')
        ).order_by('name')
        choices = choices.filter(name__icontains=q)
        return choices


class AutocompleteTemplates(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        project = self.forwarded.get('project', None)
        qms_process_model = self.forwarded.get('qms_process_model', None)
        try:
            obj = ProjectTemplateProcessModel.objects.get(project=project, qms_process_model=qms_process_model)
            choices = TemplateMaster.objects.filter(id=obj.template_id)
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
        # print chapter
        try:
            user = QASheetHeader.objects.filter \
                (project=project, chapter=chapter).values_list('author', flat=True)[0]

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
                print str(e)
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
            obj = QASheetHeader.objects.filter(project=project, chapter=chapter)[0]
            component = ComponentMaster.objects.filter(pk=obj.chapter_component.component.id)

        except:
            component = None

        return component