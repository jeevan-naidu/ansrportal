from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from MyANSRSource.models import Project, Chapter


class TemplateMaster(models.Model):

    name = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='template_master_created_by')
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='template_master_updated_by')
    active = models.BooleanField(blank=False, default=True, verbose_name="Is Active?")

    class Meta:
        verbose_name_plural = "1. Template Master"

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.name


class ProjectTemplate(models.Model):

    project = models.ForeignKey(Project)
    template = models.ForeignKey(TemplateMaster)
    created_by = models.ForeignKey(User, related_name='project_template_created_by')
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='project_template_updated_by')

    class Meta:
        verbose_name_plural = "2. Project Template"

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % (str(self.project) + " - " + str(self.template))


class DefectTypeMaster(models.Model):

    name = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='defect_type_master_created_by')
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='defect_type_master_updated_by')

    class Meta:
        verbose_name_plural = "3. Defect Type Master"

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.name


class SeverityLevelMaster(models.Model):

    name = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='severity_level_master_created_by')
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='severity_level_master_updated_by')
    active = models.BooleanField(blank=False, default=True, verbose_name="Is Active?")

    class Meta:
        verbose_name_plural = "4. Severity Level Master"

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.name


class DefectClassificationMaster(models.Model):

    name = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='defect_classification_master_created_by')
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='defect_classification_master__updated_by')
    active = models.BooleanField(blank=False, default=True, verbose_name="Is Active?")

    class Meta:
        verbose_name_plural = "5. Defect Classification Master"

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.name


class ReviewerMaster(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "6. Reviewer Master"

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.name


class ReviewerGroup(models.Model):
    name = models.CharField(max_length=100)
    review_master = models.ForeignKey(ReviewerMaster)

    class Meta:
        verbose_name_plural = "7. Reviewer Group"

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % self.name


class DefectSeverityLevel(models.Model):

    template = models.ForeignKey(TemplateMaster)
    defect_type = models.ForeignKey(ProjectTemplate)
    severity_level = models.ForeignKey(SeverityLevelMaster)
    defect_classification = models.ForeignKey(DefectClassificationMaster)
    reviewer_group = models.ForeignKey(ReviewerGroup)

    class Meta:
        verbose_name_plural = "8. Defect Severity Level"

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % (str(self.defect_type) + ": " +
                       str(self.severity_level) + ": " + str(self.defect_classification))


class ProjectChapterReviewerRelationship(models.Model):
    project = models.ForeignKey(Project)
    chapter = models.ForeignKey(Chapter, blank=False,
                                verbose_name="Chapter/Subtitle", null=True)
    author = models.ForeignKey(User, related_name='project_chapter_reviewer_relationship_author')
    review_group = models.ForeignKey(ReviewerGroup)
    reviewed_by = models.ForeignKey(User, related_name='project_chapter_reviewer_relationship_reviewed_by')
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='project_chapter_reviewer_relationship_created_by')
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='project_chapter_reviewer_relationship_updated_by')

    class Meta:
        verbose_name_plural = "9. Project Chapter Reviewer Relationship"

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % (str(self.project) + ": " +
                       str(self.chapter) +
                       ": " + str(self.author) + ": " + str(self.review_group) + ": " + str(self.reviewed_by))


class ReviewerReport(models.Model):
    project_chapter_reviewer_relationship = models.ForeignKey(ProjectChapterReviewerRelationship)
    review_item = models.CharField(max_length=100)
    defect = models.TextField()
    defect_severity_level = models.ForeignKey(DefectSeverityLevel)
    is_fixed = models.BooleanField(blank=False, default=True, verbose_name="Is Fixed?")
    fixed_by = models.ForeignKey(User, related_name='reviewer_report_fixed_by')
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='reviewer_report_created_by')
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='reviewer_report_updated_by')
    remarks = models.TextField()

    class Meta:
        verbose_name_plural = "10.Reviewer Report"

    def __unicode__(self):
        """ return unicode strings """
        return '%s' % str(self.project_chapter_reviewer_relationship )



