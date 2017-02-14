from django.contrib.auth.models import User
from django.db.models import Q
from MyANSRSource.models import Book, Project, Chapter, ProjectTeamMember
from QMS.models import QASheetHeader
from dal import autocomplete


class AutocompleteUser(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = User.objects.filter(
            Q(is_superuser=False) & Q(is_active=True)
        )

        choices = choices.filter(email__icontains=q)
        return choices


class AutocompleteBook(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = Book.objects.filter(
            name__icontains=q,
            active=True
        )
        return choices


class AutocompleteProjects(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = Project.objects.filter(
            Q(name__icontains=q) | Q(projectId__icontains=q)
        )
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

        except Exception, e:
            print str(e)
            qs = None
        #
        # if self.q:
        #     qs = qs.filter(pk=user)

        return qs


# for first screen in qms
class AutoCompleteAssignUserProjectSpecific(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = User.objects.all()

        project = self.forwarded.get('project', None)

        try:
            user = ProjectTeamMember.objects.filter \
                (project=project).values_list('member_id', flat=True)
            qs = qs.filter(pk=user)

        except Exception, e:
            print str(e)
            qs = None
        #
        # if self.q:
        #     qs = qs.filter(pk=user)

        return qs
