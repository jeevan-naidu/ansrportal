from django.contrib import admin
from .models import *
from simple_history.admin import SimpleHistoryAdmin
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
admin.site.register(QASheetHeader, SimpleHistoryAdmin)
admin.site.register(ReviewReport, SimpleHistoryAdmin)
admin.site.register(QMSProcessModel)
admin.site.register(ProjectTemplateProcessModel)
admin.site.register(ComponentMaster)
admin.site.register(ChapterComponent)
