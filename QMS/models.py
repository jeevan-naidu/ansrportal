from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from MyANSRSource.models import Project, Chapter


class TimeStampAbstractModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='%(class)s_created_by')
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='%(class)s_updated_by')

    class Meta:
        abstract = True


class NameMasterAbstractModel(models.Model):

    name = models.CharField(max_length=100)
    active = models.BooleanField(blank=False, default=True, verbose_name="Is Active?")

    class Meta:
        abstract = True

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.name


class TemplateMaster(NameMasterAbstractModel, TimeStampAbstractModel):

    pass


class ProjectTemplate(TimeStampAbstractModel):

    project = models.ForeignKey(Project)
    template = models.ForeignKey(TemplateMaster)

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % (str(self.project) + " - " + str(self.template))


class DefectTypeMaster(NameMasterAbstractModel, TimeStampAbstractModel):

    pass


def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.name


class SeverityLevelMaster(NameMasterAbstractModel, TimeStampAbstractModel):

    pass


def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.name


class DefectClassificationMaster(NameMasterAbstractModel, TimeStampAbstractModel):

    pass


def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.name


class ReviewerMaster(NameMasterAbstractModel):

    pass


def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.name


class ReviewerGroup(models.Model):
    name = models.CharField(max_length=100)
    review_master = models.ForeignKey(ReviewerMaster)

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.name


class DefectSeverityLevel(TimeStampAbstractModel):

    template = models.ForeignKey(TemplateMaster)
    severity_type = models.ForeignKey(DefectTypeMaster)
    severity_level = models.ForeignKey(SeverityLevelMaster)
    defect_classification = models.ForeignKey(DefectClassificationMaster)
    reviewer_group = models.ForeignKey(ReviewerGroup)

    # def __unicode__(self):
    #     """ return unicode strings """
    #     return '%s' % ( str(self.severity_type)+": " + str(self.severity_level) + ": "
    #
    #                    + str(self.defect_classification))


class ProjectChapterReviewerRelationship(TimeStampAbstractModel):
    project = models.ForeignKey(Project)
    chapter = models.ForeignKey(Chapter, blank=False,
                                verbose_name="Chapter/Subtitle", null=True)
    questions = models.IntegerField(default=0)
    author = models.ForeignKey(User, related_name='project_chapter_reviewer_relationship_author')
    review_group = models.ForeignKey(ReviewerGroup)
    reviewed_by = models.ForeignKey(User, related_name='project_chapter_reviewer_relationship_reviewed_by')

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % (str(self.project) +
                       " : " + str(self.review_group) +
                       " : " + str(self.chapter)
                       )


class ReviewerReport(TimeStampAbstractModel):
    project_chapter_reviewer_relationship = models.ForeignKey(ProjectChapterReviewerRelationship)
    review_item = models.CharField(max_length=100)
    defect = models.TextField()
    defect_severity_level = models.ForeignKey(DefectSeverityLevel)
    is_fixed = models.BooleanField(blank=False, default=True, verbose_name="Is Fixed?")
    fixed_by = models.ForeignKey(User, related_name='reviewer_report_fixed_by')

    remarks = models.TextField()

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % str(self.project_chapter_reviewer_relationship)



