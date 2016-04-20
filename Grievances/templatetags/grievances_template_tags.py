from django import template
from Grievances.models import SATISFACTION_CHOICES
register = template.Library()
from datetime import datetime

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
    
    current_time = datetime.now().time().hour
    diff = current_time - registered_date
    if diff <= 24:
        return True
    else:
        return False


#register.filter('GetFileNamefromPath', GetFileNamefromPath)