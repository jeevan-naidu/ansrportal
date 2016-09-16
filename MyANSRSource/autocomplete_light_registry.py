from django.contrib.auth.models import User
from django.db.models import Q
from MyANSRSource.models import Book, Project
from dal import autocomplete


class AutocompleteUser(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = User.objects.filter(
            Q(is_superuser=False)
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

