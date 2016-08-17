#import autocomplete_light
from django.contrib.auth.models import User
from django.db.models import Q
from MyANSRSource.models import Book, Project
from dal import autocomplete


class AutocompleteUser(autocomplete.Select2QuerySetView):
    autocomplete_js_attributes = {'placeholder': 'Enter a member name'}

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = User.objects.filter(
            Q(is_superuser=False)
        )

        choices = choices.filter(email__icontains=q)
        return choices

#autocomplete_light.register(User, AutocompleteUser)


class AutocompleteBook(autocomplete.Select2QuerySetView):
    autocomplete_js_attributes = {'placeholder': 'Enter a book name'}

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = Book.objects.filter(
            name__icontains=q,
            active=True
        )
        return choices

#autocomplete_light.register(Book, AutocompleteBook)


class AutocompleteProjects(autocomplete.Select2QuerySetView):
    autocomplete_js_attributes = {'placeholder': 'Enter a Project name /Project Id'}

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = Project.objects.filter(
            Q(name__icontains=q) | Q(projectId__icontains=q)
        )
        return choices

#autocomplete_light.register(Project, AutocompleteProjects)
