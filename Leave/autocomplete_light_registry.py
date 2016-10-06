from dal import autocomplete
from django.db.models import Q
from employee.models import Employee


class AutocompleteUserSearch(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        user = self.request.user.id
        emp = Employee.objects.get(user_id=user)
        q = self.request.GET.get('q', '')
        if self.request.user.groups.filter(name='myansrsourceHR').exists():
            user_list = Employee.objects.filter(user__is_active=True,
                                                  user__first_name__icontains=q)
        else:
            user_list = Employee.objects.filter((Q(manager_id=emp.employee_assigned_id) |
                                                  Q(employee_assigned_id=emp.employee_assigned_id)),
                                                Q(user__first_name__icontains=q),
                                                Q(user__is_active=True)
                                                )

        return user_list
