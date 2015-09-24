from functools import wraps
from django.shortcuts import redirect

"""
Decorator to check the logged in user has
eligible for 360 Degree Feedback.
If eligible it will show normal peer screens
If not will redirect to dashboard
"""


def eligible_360(view_func):
    def _decorator(request, *args, **kwargs):
        if request.user.employee.is_360eligible:
            response = view_func(request, *args, **kwargs)
            return response
        else:
            return redirect('/myansrsource/dashboard')
    return wraps(view_func)(_decorator)
