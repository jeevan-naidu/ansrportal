from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(TemplateMaster)
admin.site.register(TemplateProcessReview)
admin.site.register(DefectTypeMaster)
admin.site.register(SeverityLevelMaster)
admin.site.register(DefectClassificationMaster)
admin.site.register(ReviewMaster)
admin.site.register(ReviewGroup)
admin.site.register(WorkPacketMaster)
admin.site.register(DefectSeverityLevel)
admin.site.register(QASheetHeader)
admin.site.register(ReviewReport)
admin.site.register(QMSProcessModel)
