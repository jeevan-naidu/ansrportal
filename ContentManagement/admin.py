from django.contrib import admin
from models import MediaContent, MediaContentTypes, Notice, NoticeTypes
# Register your models here.
admin.site.register(MediaContent)
admin.site.register(MediaContentTypes)
admin.site.register(Notice)
admin.site.register(NoticeTypes)

