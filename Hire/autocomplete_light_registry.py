from dal import autocomplete
from models import Count, MRF
from employee.models import Employee
from django.contrib.auth.models import User


class AutoCompleteRequisitionSearch(autocomplete.Select2QuerySetView):
    autocomplete_js_attributes = {'placeholder': 'Enter a member name'}

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        choices = MRF.objects.filter(requisition_number__icontains=q)
        return choices



class AutocompleteUserHireSearch(autocomplete.Select2QuerySetView):
    autocomplete_js_attributes = {'placeholder': 'Enter a member name'}

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        user_list = User.objects.filter(is_active=True,
                                                  first_name__icontains=q)
        return user_list




class AutoCompleteRequisitionSearchUser(autocomplete.Select2QuerySetView):
    autocomplete_js_attributes = {'placeholder': 'Enter a member name'}

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        avaliable_choice = Count.objects.filter(recruiter = self.request.user.id).values('id')
        choices = Count.objects.filter(requisition_number__requisition_number__icontains=q,
                                       id__in=avaliable_choice)
        return choices

