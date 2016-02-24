from django import template
register = template.Library()

@register.filter
def GetFileNamefromPath(filepath):
    
    return filepath.split("/")[-1]

@register.filter
def GetFileTypeFromName(filename):
    
    return filename.split(".")[-1]


#register.filter('GetFileNamefromPath', GetFileNamefromPath)