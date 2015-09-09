import autocomplete_light
from django.contrib.auth.models import User
from django.db.models import Q
from MyANSRSource.models import Book, Project


class AutocompleteUser(autocomplete_light.AutocompleteModelBase):
    autocomplete_js_attributes = {'placeholder': 'Enter a member name'}

    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        choices = self.choices.filter(
            Q(is_superuser=False)
        )

        choices = choices.filter(email__icontains=q)
        return self.order_choices(choices)[0:self.limit_choices]

autocomplete_light.register(User, AutocompleteUser)


class AutocompleteBook(autocomplete_light.AutocompleteModelBase):
    autocomplete_js_attributes = {'placeholder': 'Enter a book name'}

    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        choices = self.choices.filter(name__icontains=q)
        return self.order_choices(choices)[0:self.limit_choices]

autocomplete_light.register(Book, AutocompleteBook)
