from dal import autocomplete
from Grievances.models import Grievances


class AutocompleteGrievanceAdmin(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = Grievances.objects.filter(
            grievance_id__icontains=q
        )

        return choices
