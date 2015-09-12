from functools import wraps
from django.shortcuts import redirect
from .models import FB360
from datetime import date

"""
Decorator to check feedback date has
expired or not
If eligible it will show normal feedback requestee list screen
If not will redirect to dashboard
"""


def fb_eligible(view_func):
    def _decorator(request, *args, **kwargs):
        fbObj = FB360.objects.filter(year=date.today().year)
        if (fbObj[0].start_date <= date.today() and
                fbObj[0].end_date >= date.today()):
            response = view_func(request, *args, **kwargs)
            return response
        else:
            return redirect('/myansrsource/dashboard')
    return wraps(view_func)(_decorator)
