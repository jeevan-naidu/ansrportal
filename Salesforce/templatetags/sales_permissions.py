from django import template
from django.conf import settings
register = template.Library()

@register.filter('IsSalesforceAdmin')
def IsSalesforceAdmin(user):
    UserGroupsList = user.groups.all().values_list('name', flat=True)
    return settings.SALESFORCE_ADMIN_GROUP_NAME in UserGroupsList