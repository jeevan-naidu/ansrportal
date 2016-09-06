import autocomplete_light
from models import MRF
from employee.models import Employee
from django.contrib.auth.models import User


class AutoCompleteRequisitionSearch(autocomplete_light.AutocompleteModelBase):
    autocomplete_js_attributes = {'placeholder': 'Enter a member name'}

    def choices_for_request(self):
        # userlist = Employee.objects.filter().values('user_id')
        q = self.request.GET.get('q', '')
        choices = self.choices.filter(requisition_number__icontains=q)
        # choices = choices.filter(id__in=userlist)
        return self.order_choices(choices)[0:self.limit_choices]

autocomplete_light.register(MRF, AutoCompleteRequisitionSearch)

class AutocompleteUserHireSearch(autocomplete_light.AutocompleteModelBase):
    autocomplete_js_attributes = {'placeholder': 'Enter a member name'}

    def choices_for_request(self):

        userlist = Employee.objects.filter().values('user_id')
        q = self.request.GET.get('q', '')
        choices = self.choices.filter(first_name__icontains=q)
        choices = choices.filter(id__in=userlist)
        return self.order_choices(choices)[0:self.limit_choices]

autocomplete_light.register(User, AutocompleteUserHireSearch)

