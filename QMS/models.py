from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from MyANSRSource.models import Project, Chapter
from simple_history.models import HistoricalRecords

fixed_status = (('', '------'), ('fixed', 'Fixed'), ('fix_not_required', 'Fix Not Required'))


class TimeStampAbstractModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='%(class)s_created_by')
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='%(class)s_updated_by', blank=True, null=True)

    class Meta:
        abstract = True


class NameMasterAbstractModel(models.Model):

    name = models.CharField(max_length=100)
    is_active = models.BooleanField(blank=False, default=True, verbose_name="Is Active?")

    class Meta:
        abstract = True

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.name


class TemplateMaster(NameMasterAbstractModel, TimeStampAbstractModel):

    pass


class QMSProcessModel(NameMasterAbstractModel, TimeStampAbstractModel):
    pass


class ProjectTemplateProcessModel(TimeStampAbstractModel):

    project = models.ForeignKey(Project)
    template = models.ForeignKey(TemplateMaster)
    lead_review_status = models.BooleanField(
        default=False,
        null=False,
        verbose_name=" Is Lead Review Completed "
    )
    qms_process_model = models.ForeignKey(QMSProcessModel)

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % (str(self.project) + " - " + str(self.template))


class DefectTypeMaster(NameMasterAbstractModel, TimeStampAbstractModel):

    pass


class SeverityLevelMaster(NameMasterAbstractModel, TimeStampAbstractModel):
    penalty_count = models.DecimalField(blank=False, decimal_places=1, max_digits=2, verbose_name="Penalty Count",
                                        null=False)
    pass


class DefectClassificationMaster(NameMasterAbstractModel, TimeStampAbstractModel):

    pass


class ReviewMaster(NameMasterAbstractModel):

    pass


class WorkPacketMaster(NameMasterAbstractModel, TimeStampAbstractModel):
    pass


class ComponentMaster(NameMasterAbstractModel, TimeStampAbstractModel):
    pass


class ReviewGroup(models.Model):
    name = models.CharField(max_length=100)
    review_master = models.ForeignKey(ReviewMaster)

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.name


class DefectSeverityLevel(TimeStampAbstractModel):

    template = models.ForeignKey(TemplateMaster)
    severity_type = models.ForeignKey(DefectTypeMaster)
    severity_level = models.ForeignKey(SeverityLevelMaster)
    defect_classification = models.ForeignKey(DefectClassificationMaster)
    review_master = models.ForeignKey(ReviewMaster)

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.id
        return '%s' % (str(self.severity_type)+": " + str(self.severity_level) + ": "
                       + str(self.defect_classification))


class ChapterComponent(TimeStampAbstractModel):
    chapter = models.ForeignKey(Chapter, blank=False, verbose_name="Chapter/Subtitle", null=False)
    component = models.ForeignKey(ComponentMaster, blank=False, verbose_name="Component", null=False)

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.id


class QASheetHeader(TimeStampAbstractModel):
    project = models.ForeignKey(Project)
    chapter = models.ForeignKey(Chapter, blank=False,
                                verbose_name="Chapter/Subtitle", null=True)
    chapter_component = models.ForeignKey(ChapterComponent, blank=True, verbose_name="Chapter&Component", null=True)

    work_packet = models.ForeignKey(WorkPacketMaster, verbose_name="work packet (output)", blank=True, null=True, )
    count = models.IntegerField(verbose_name="work packet count", default=0)
    author = models.ForeignKey(User, related_name='QASheetHeader_author', blank=True, null=True,)
    review_group = models.ForeignKey(ReviewGroup)
    reviewed_by = models.ForeignKey(User, related_name='QASheetHeader_reviewed_by')
    review_group_status = models.BooleanField(
        default=False,
        null=False,
        verbose_name=" Is Review Completed "
    )
    author_feedback_status = models.BooleanField(
        default=False,
        null=False,
        verbose_name=" Is author feedback Completed "
    )
    order_number = models.IntegerField(blank=False,
                                       verbose_name="Review tab Order", null=False)
    history = HistoricalRecords()

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % (str(self.project) +
                       " : " + str(self.review_group) +
                       " : " + str(self.chapter)
                       )


class ReviewReport(TimeStampAbstractModel):
    QA_sheet_header = models.ForeignKey(QASheetHeader)
    review_item = models.CharField(max_length=100)
    defect = models.TextField()
    screen_shot = models.FileField(upload_to='qms', blank=True, null=True, verbose_name="upload screen shot")
    defect_severity_level = models.ForeignKey(DefectSeverityLevel)
    is_fixed = models.CharField(max_length=50, blank=True, null=True, choices=fixed_status, verbose_name="Is Fixed?")
    fixed_by = models.ForeignKey(User, related_name='reviewer_report_fixed_by', blank=True, null=True,)
    remarks = models.TextField(blank=True, null=True,)
    is_active = models.BooleanField(blank=False, default=True, verbose_name="Is Active?")
    history = HistoricalRecords()

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % str(self.QA_sheet_header)


class TemplateProcessReview(TimeStampAbstractModel):
    template = models.ForeignKey(TemplateMaster)
    qms_process_model = models.ForeignKey(QMSProcessModel)
    review_group = models.ForeignKey(ReviewGroup)
    is_mandatory = models.BooleanField(default=False, verbose_name="Is Mandatory")

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.id
