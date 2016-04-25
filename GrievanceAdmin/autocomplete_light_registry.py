import autocomplete_light
from Grievances.models import Grievances


class AutocompleteGrievanceAdmin(autocomplete_light.AutocompleteModelBase):
    autocomplete_js_attributes = {'placeholder': 'Enter a Grievance Id'}

    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        choices = self.choices.filter(
            grievance_id__icontains=q
        )

        return self.order_choices(choices)[0:self.limit_choices]

autocomplete_light.register(Grievances, AutocompleteGrievanceAdmin)
