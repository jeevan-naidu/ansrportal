from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(TemplateMaster)
admin.site.register(ProjectTemplate)
admin.site.register(DefectTypeMaster)
admin.site.register(SeverityLevelMaster)
admin.site.register(DefectClassificationMaster)
admin.site.register(ReviewerMaster)
admin.site.register(ReviewerGroup)
admin.site.register(DefectSeverityLevel)
admin.site.register(ProjectChapterReviewerRelationship)
admin.site.register(ReviewerReport)
