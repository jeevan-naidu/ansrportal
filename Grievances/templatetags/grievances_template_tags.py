from django import template
register = template.Library()
from datetime import datetime

@register.filter
def GetFileNamefromPath(filepath):
    
    return filepath.split("/")[-1]

@register.filter
def GetFileTypeFromName(filename):
    
    return filename.split(".")[-1]

@register.filter
def IsNew(registered_date):
    
    current_time = datetime.now().time().hour
    diff = current_time - registered_date
    if diff <= 24:
        return True
    else:
        return False


#register.filter('GetFileNamefromPath', GetFileNamefromPath)