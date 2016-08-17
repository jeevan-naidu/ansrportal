#import autocomplete_light
from dal import autocomplete
from Grievances.models import Grievances


class AutocompleteGrievanceAdmin(autocomplete.Select2QuerySetView):
    autocomplete_js_attributes = {'placeholder': 'Enter a Grievance Id'}

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = Grievances.filter(
            grievance_id__icontains=q
        )

        return choices #self.order_choices(choices)[0:self.limit_choices]

#autocomplete_light.register(Grievances, AutocompleteGrievanceAdmin)
