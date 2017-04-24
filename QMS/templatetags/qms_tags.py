from django import template
from django.contrib.auth.models import Group
from django.conf import settings
import employee
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q, Sum
from QMS.models import *
from MyANSRSource.models import *
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
        print "pk" , pk
        s = SeverityLevelMaster.objects.get(id=pk)
    except ObjectDoesNotExist as e:
        print  "get_severity_level" , str(e)
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


@register.simple_tag
def get_severity_count(project, name, template_id):
    s = 0
    try:
        severity_level_obj = SeverityLevelMaster.objects.get(name__icontains=name)
        review_report_obj = ReviewReport.objects.filter(QA_sheet_header__in=QASheetHeader.objects.filter(
            project=project).values_list('id', flat=True), defect_severity_level__severity_level=severity_level_obj).\
            values('id', 'defect_severity_level__severity_level__name').exclude(is_active=False). \
            annotate(s_count=Count('defect_severity_level'))
        # dsl = DSLTemplateReviewGroup.objects.filter(template_id=template_id,
        # obj = DefectSeverityLevel.objects.filter(template_id=template_id,
        #                                          severity_level=severity_level_obj)
        # review_report = ReviewReport.objects.filter(defect_severity_level__in=obj,
        #                                             QA_sheet_header=QASheetHeader.objects.filter(project=project)[0]).\
        #     values('id', 'defect_severity_level__severity_level__name').\
        #     annotate(s_count=Count('defect_severity_level'))
        for v in review_report_obj:
            for key, value in v.iteritems():
                if key is 's_count':
                    s += value
    except Exception as e:
        print "get_severity_count " , str(e)
        logger.error("qms format{0}", str(e))
    return s


@register.simple_tag
def get_defect_density(s1, s2, s3, q_count):
    # print s1, s2, s3, q_count
    if q_count == 0:
        return 0
    else:
        s1_dd = (s1 * 0.5)/q_count
        s2_dd = (s2 * 0.3)/q_count
        s3_dd = (s3 * 0.2)/q_count
        return str(round(((s1_dd + s2_dd + s3_dd)*100), 2))


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


@register.simple_tag
def is_project_manager(project, user):
    try:
        s = ProjectManager.objects.filter(project=project, user=user).exists()
    except Exception as e:
        s = False
    return s


@register.simple_tag
def get_project_status(project):
    can_show_button = QASheetHeader.objects.filter((Q(review_group_status=False) | Q(author_feedback_status=False)),
                                                   project=project).exists()
    if not can_show_button:
        obj = ProjectTemplateProcessModel.objects.get(project=project)
        if obj.lead_review_status is False:
            can_show_button = True
    chapter_count = Chapter.objects.filter(book__project=project).count()
    qa_chapter_count = QASheetHeader.objects.filter(project=project).values('chapter').distinct().count()
    if chapter_count != qa_chapter_count:
        difference = chapter_count - qa_chapter_count
    else:
        difference = 0
    return can_show_button, difference

