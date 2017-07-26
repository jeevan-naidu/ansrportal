from django.contrib.auth.models import User
from django.db.models import Q
from MyANSRSource.models import Book, Project, qualitysop, ProjectAsset, ProjectScope, Milestone, ProjectSopTemplate, \
    Role
from CompanyMaster.models import Practice, SubPractice, DataPoint
from dal import autocomplete
from MyANSRSource.models import Milestone
from QMS.models import TemplateProcessReview, TemplateMaster



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

class AutocompleteProjectAsset(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = ProjectAsset.objects.filter(Asset__icontains=q)
        return choices


class AutocompleteDatapointName(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = DataPoint.objects.filter(name__icontains=q, is_active=True)
        return choices


class AutocompletesubPracticeName(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = SubPractice.objects.filter(name__icontains=q)
        return choices


class Autocompleteprojecttemplate(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        value = self.request.session['name']
        try:
            templatename = TemplateMaster.objects.filter(id__in=TemplateProcessReview.objects.filter(qms_process_model=value).values_list('template'))
            print "templ", templatename
        except Exception as e:
            print Exception
        return templatename


class AutocompleteQualitySOP(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        try:
            choices = qualitysop.objects.filter(name__icontains=q)
        except Exception as e:
            print e
        return choices


class Autocompleteprojectscope(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = ProjectScope.objects.filter(scope__icontains=q)
        return choices


class AutocompleteMilestonetype(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = Milestone.objects.filter(name__icontains=q)
        return choices


class AutocompleteMilestonetype(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = Milestone.objects.filter(name__icontains=q)
        return choices


class AutocompleteRole(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = Role.objects.filter(role__icontains=q, is_active=True)
        return choices