from django import template

register = template.Library()


@register.filter('manage_project')
def manage_project(user):
    return user.has_perm('manage_project')


@register.filter('approve_timesheet')
def approve_timesheet(user):
    return user.has_perm('approve_timesheet')


@register.filter('manage_milestones')
def manage_milestones(user):
    return user.has_perm('manage_milestones')
