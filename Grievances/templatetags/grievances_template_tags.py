from django import template
from Grievances.models import SATISFACTION_CHOICES
register = template.Library()

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

#register.filter('GetFileNamefromPath', GetFileNamefromPath)