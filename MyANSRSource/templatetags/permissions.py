from django import template
from django.contrib.auth.models import Group

register = template.Library()
from django.conf import settings


@register.filter('create_project')
def manage_project(user):
    return user.has_perm('MyANSRSource.create_project')


@register.filter('manage_project')
def manage_project(user):
    return user.has_perm('MyANSRSource.manage_project')


@register.filter('approve_timesheet')
def approve_timesheet(user):
    return user.has_perm('MyANSRSource.approve_timesheet')


@register.filter('manage_milestones')
def manage_milestones(user):
    return user.has_perm('MyANSRSource.manage_milestones')


@register.filter(name='has_group')  # added for grievance admin module
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
    except group.DoesNotExist:
        group = None
    return True if group in user.groups.all() else False


@register.filter('IsMilestoneReportsAdmin')
def IsMilestoneReportsAdmin(user):
    UserGroupsList = user.groups.all().values_list('name', flat=True)
    return settings.MILESTONE_REPORTS_ADMIN_GROUP_NAME in UserGroupsList


@register.filter('IsSalesforceAdmin')
def IsSalesforceAdmin(user):
    UserGroupsList = user.groups.all().values_list('name', flat=True)
    return settings.SALESFORCE_ADMIN_GROUP_NAME in UserGroupsList
