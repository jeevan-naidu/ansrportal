from django import template
from Grievances.models import SATISFACTION_CHOICES
register = template.Library()
from datetime import datetime
from django.utils.timezone import localtime
from django.utils.timezone import get_default_timezone
@register.filter
def GetFileNamefromPath(filepath):
    
    return filepath.split("/")[-1]

@register.filter
def GetFileTypeFromName(filename):
    
    return filename.split(".")[-1]

@register.filter
def satisfaction_level(value):
    for k, v in SATISFACTION_CHOICES:
        if k.strip() == value.strip():
            return v

@register.filter
def IsNew(registered_date):
    import ipdb;ipdb.set_trace()
    current_date = datetime.now().replace(tzinfo=get_default_timezone())
    registered_date = localtime(registered_date)
    diff = current_date - registered_date
    if diff.days < 5:
        return True
    else:
        return False


#register.filter('GetFileNamefromPath', GetFileNamefromPath)