from django.contrib.auth.models import User
from django.db.models import Q
from MyANSRSource.models import Book, Project, qualitysop
from CompanyMaster.models import Practice, SubPractice
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


class AutocompletePracticeHead(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        head_id = Practice.objects.values_list('head_id')
        choices = User.objects.filter(is_active=True, id__in=head_id, first_name__icontains=q)
        return choices


class AutocompletePracticeName(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = Practice.objects.filter(name__icontains=q)
        return choices


class AutocompletesubPracticeName(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = SubPractice.objects.filter(name__icontains=q)
        return choices


class AutocompleteQualitySOP(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        try:
            choices = qualitysop.objects.filter(name__icontains=q)
        except Exception as e:
            print e
        return choices
