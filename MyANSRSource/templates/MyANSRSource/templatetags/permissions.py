from django import template
from django.contrib.auth.models import Group ,User
from django.conf import settings
import employee
import ExitApp
register = template.Library()


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


@register.filter(name='has_url')  # added for timesheet entry module
def has_url(actual_path, url):
    if url in actual_path:
        return True
    else:
        return False


@register.filter('IsMilestoneReportsAdmin')
def IsMilestoneReportsAdmin(user):
    UserGroupsList = user.groups.all().values_list('name', flat=True)
    return settings.MILESTONE_REPORTS_ADMIN_GROUP_NAME in UserGroupsList


@register.filter('IsActiveShortAttendance')
def IsActiveShortAttendance(value):
    return settings.LEAVE_SHORT_ATTENDANCE_ISACTIVE

@register.filter(name='isManager')  # added for grievance admin module
def choose_reportee(user):
    if user.is_anonymous:  # condition added to handled employee dont have entry in employee table
        return 0
    myReportee = employee.models.Employee.objects.filter(
        manager=user.employee)
    is_manager = 0
    if myReportee:
        is_manager = 1
    return is_manager


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

@register.filter
def get_item(dictionary, key):
    # print dictionary
    try:
        s = dictionary.get(key)
    except:
        s = 0
    if s is None:
        s = 0
    return s


@register.simple_tag
def get_full_name(member_id):
    obj = User.objects.get(pk=member_id)
    return ''.joint(obj.first_name, obj.last_name)