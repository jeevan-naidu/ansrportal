from functools import wraps
from django.shortcuts import redirect
import employee

"""
Decorator to check the logged in user has
reportees or not.
If eligible it will show normal choose reportee screen
If not will redirect to dashboard
"""


def is_manager(view_func):
    def _decorator(request, *args, **kwargs):
        myReportees = employee.models.Employee.objects.filter(
            manager=request.user.employee)
        if myReportees:
            response = view_func(request, *args, **kwargs)
            return response
        else:
            return redirect('/myansrsource/dashboard')
    return wraps(view_func)(_decorator)
