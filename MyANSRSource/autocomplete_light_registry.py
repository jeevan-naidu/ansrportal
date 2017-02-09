from django.contrib.auth.models import User
from django.db.models import Q
from MyANSRSource.models import Book, Project
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
        choices = User.objects.filter(first_name__icontains=q)
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

