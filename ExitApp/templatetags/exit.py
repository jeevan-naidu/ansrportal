from django import template
from django.contrib.auth.models import Group
from django.conf import settings
import employee
register = template.Library()

@register.filter(name='has_group')  # added for grievance admin module
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
    except group.DoesNotExist:
        group = None
    return True if group in user.groups.all() else False


@register.filter('IsManager')
def IsManager(user):
    UserGroupsList = user.groups.all().values_list('name', flat=True)
    return settings.MANAGER in UserGroupsList

@register.filter('DirectReportee')
def DirectReportee(user, request):
    mgrid = employee.models.Employee.objects.get(user_id=request.id)
    reportee = employee.models.Employee.objects.filter(manager_id=mgrid, user_id=user)
    if reportee:
        reportee_flag = 1
    else:
        reportee_flag = 0

    return reportee_flag
