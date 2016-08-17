#import autocomplete_light
from dal import autocomplete

from django.contrib.auth.models import User
from django.db.models import Q
from employee.models import Employee

class AutocompleteUserSearch(autocomplete.Select2QuerySetView):
    autocomplete_js_attributes = {'placeholder': 'Enter a member name'}

    def get_queryset(self):
        user = self.request.user.id
        emp = Employee.objects.get(user_id = user)
        q = self.request.GET.get('q', '')
        if self.request.user.groups.filter(name='myansrsourceHR').exists() or self.request.user.is_superuser:
            userlist = Employee.objects.filter(user__first_name__icontains=q).values('user_id','user__first_name').exclude(user_id__is_superuser=True)
        else:
            userlist = Employee.objects.filter(Q(user__first_name__icontains=q) &( Q(manager_id= emp.employee_assigned_id) | Q(employee_assigned_id= emp.employee_assigned_id) )).exclude(user_id__is_superuser=True)
        q = self.request.GET.get('q', '')
        """choices = self.choices.filter(
            Q(is_superuser=False)

        )"""

        #choices = userlist.filter(first_name__icontains=q)
        #choices = choices.filter(id__in=userlist)
        return userlist #self.order_choices(choices)[0:self.limit_choices]

#autocomplete_light.register(User, AutocompleteUserSearch)
