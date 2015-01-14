import autocomplete_light
from django.contrib.auth.models import User
from django.db.models import Q


class AutocompleteUser(autocomplete_light.AutocompleteModelBase):
    autocomplete_js_attributes = {'placeholder': 'Enter a member name'}

    def choices_for_request(self):
        choices = self.choices.filter(
            Q(is_superuser=False)
        )
        return self.order_choices(choices)[0:self.limit_choices]

autocomplete_light.register(User, AutocompleteUser)
