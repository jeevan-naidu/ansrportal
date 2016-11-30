from django import template
from django.contrib.auth.models import Group
from django.conf import settings
import employee
from QMS.models import *

register = template.Library()


@register.filter
def get_item(dictionary, key):
    s = dictionary.get(key)
    if s is None:
        s = 0
    return s


def is_in(var, args):
    if args is None:
        return False
    arg_list = [arg.strip() for arg in args.split(',')]
    return var in arg_list


register.filter(is_in)


@register.filter('get_severity_level')
def get_severity_level(id, pk):
    return SeverityLevelMaster.objects.get(id=pk)


@register.filter('get_severity_type')
def get_severity_type(id, pk):
    return DefectTypeMaster.objects.get(id=pk)


@register.filter('get_severity_classification')
def get_severity_classification(id, pk):
    return DefectClassificationMaster.objects.get(id=pk)
