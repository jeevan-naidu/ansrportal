import autocomplete_light
from django.contrib.auth.models import User
from django.db.models import Q
from employee.models import Employee

class AutocompleteUserSearch(autocomplete_light.AutocompleteModelBase):
    autocomplete_js_attributes = {'placeholder': 'Enter a member name'}

    def choices_for_request(self):
        user = self.request.user.id
        emp = Employee.objects.get(user_id = user)
        if self.request.user.groups.filter(name='LeaveAdmin').exists() or self.request.user.is_superuser:
            userlist = Employee.objects.filter().values('user_id')
        else:
            userlist = Employee.objects.filter(Q(manager_id= emp.employee_assigned_id) | Q(employee_assigned_id= emp.employee_assigned_id) ).values('user_id')
        q = self.request.GET.get('q', '')
        choices = self.choices.filter(
            Q(is_superuser=False)

        )

        choices = choices.filter(first_name__icontains=q)
        choices = choices.filter(id__in=userlist)
        choices = choices.filter(is_active=True)
        return self.order_choices(choices)[0:self.limit_choices]

autocomplete_light.register(User, AutocompleteUserSearch)
