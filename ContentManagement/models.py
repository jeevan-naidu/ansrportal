from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
# Create your models here.


class NoticeTypes(models.Model):

    notice_type = models.CharField(max_length=100)
    active = models.BooleanField(default=True, verbose_name="Is Active?")
    created_date = models.DateTimeField(verbose_name="created On", auto_now_add=True)
    updated_date = models.DateTimeField(verbose_name="Updated On", auto_now=True)
    
    def __unicode__(self):
        return '%s' % (self.notice_type)


class Notice(models.Model):

    notice_type = models.ForeignKey(NoticeTypes)
    display_message = models.TextField(max_length=2100, validators=[MinLengthValidator(15)],
                                       help_text="Max length: 2000 characters")
    search_keywords = models.CharField(max_length=200,
                                       help_text="200 characters, each keyword seperated by comma")
    created_by = models.ForeignKey(User, verbose_name="Added By", blank=True, null=True)
    created_date = models.DateTimeField(verbose_name="created On", auto_now_add=True)
    updated_date = models.DateTimeField(verbose_name="Updated On", auto_now=True)
    active = models.BooleanField(default=True, verbose_name="Is Active?")
    
    def __unicode__(self):
        return '%s' % (self.display_message)


class MediaContentTypes(models.Model):

    media_content_type = models.CharField(max_length=100)
    active = models.BooleanField(default=True, verbose_name="Is Active?")
    created_date = models.DateTimeField(verbose_name="created On", auto_now_add=True)
    updated_date = models.DateTimeField(verbose_name="Updated On", auto_now=True)
    active = models.BooleanField(default=True, verbose_name="Is Active?")
    
    def __unicode__(self):
        return '%s' % (self.media_content_type)


class MediaContent(models.Model):

    media_content_type = models.ForeignKey(MediaContentTypes)
    media_file = models.FileField(upload_to='', blank=True, null=True, help_text="Image/video file")
    display_message = models.TextField(max_length=200, validators=[MinLengthValidator(15)],
                                       help_text="Max length: 200 characters")
    search_keywords = models.CharField(max_length=200,
                                       help_text="200 characters, each keyword seperated by comma")
    created_by = models.ForeignKey(User, verbose_name="Added By", blank=True, null=True)
    created_date = models.DateTimeField(verbose_name="created On", auto_now_add=True)
    updated_date = models.DateTimeField(verbose_name="Updated On", auto_now=True)
    active = models.BooleanField(default=True, verbose_name="Is Active?")

    def __unicode__(self):
        return '%s' % (self.display_message)