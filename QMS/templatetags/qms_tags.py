from django import template
from django.contrib.auth.models import Group
from django.conf import settings
import employee
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from QMS.models import *
import logging
logger = logging.getLogger('MyANSRSource')
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


@register.filter('get_severity_count')
def get_count(project, name):
    s = 0
    try:
        project_template_process = ProjectTemplateProcessModel.objects.get(project=project)
        severity_level_obj = SeverityLevelMaster.objects.get(name__icontains=name)
        obj = DefectSeverityLevel.objects.filter(template_id=project_template_process.template_id,
                                                 severity_level=severity_level_obj)
        review_report = ReviewReport.objects.filter(defect_severity_level__in=obj,
                                                    QA_sheet_header=QASheetHeader.objects.filter(project=project)[0]).\
            values('id', 'defect_severity_level__severity_level__name').\
            annotate(s_count=Count('defect_severity_level'))
        for v in review_report:
            for key, value in v.iteritems():
                if key is 's_count':
                    s += value
    except Exception as e:
        logger.error("qms format{0}", str(e))
    return s


@register.filter('get_question_count')
def get_question_count(project):
    s = 0
    try:
        qa_object = QASheetHeader.objects.filter(project=project).values_list('count', flat=True)
        for v in qa_object:
            s += v
    except Exception as e:
        logger.error("qms format{0}", str(e))
    return s
