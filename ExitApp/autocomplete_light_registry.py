from dal import autocomplete
from models import ResignationInfo, EmployeeFeedback, ClearanceInfo
from django.contrib.auth.models import User


class AutoCompleteRequisitionSearch(autocomplete.Select2QuerySetView):
    autocomplete_js_attributes = {'placeholder': 'Enter a member name'}

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = ResignationInfo.objects.filter(User__email__icontains=q).values_list('User_id')
        return User.objects.filter(id__in=choices)
        # return choices


class AutoCompleteResigneeSearch(autocomplete.Select2QuerySetView):
    autocomplete_js_attributes = {'placeholder': 'Enter a member name'}

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = ResignationInfo.objects.filter(User__email__icontains=q).values_list('User_id')
        return User.objects.filter(id__in=choices)

