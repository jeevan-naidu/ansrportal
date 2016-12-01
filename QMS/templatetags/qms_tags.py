from django import template
from django.contrib.auth.models import Group
from django.conf import settings
import employee
from django.core.exceptions import ObjectDoesNotExist
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
    try:
        s = SeverityLevelMaster.objects.get(id=pk)
    except ObjectDoesNotExist:
        s = None
    return s


@register.filter('get_severity_type')
def get_severity_type(id, pk):
    try:
        s = DefectTypeMaster.objects.get(id=pk)
    except ObjectDoesNotExist:
        s = None
    return s


@register.filter('get_severity_classification')
def get_severity_classification(id, pk):
    try:
        s = DefectClassificationMaster.objects.get(id=pk)
    except ObjectDoesNotExist:
        s = None
    return s


@register.filter('get_fixed_status')
def get_fixed_status(id, val):
    s = '--'
    for k, v in fixed_status:
        if k == val:
            s = v
    return s
