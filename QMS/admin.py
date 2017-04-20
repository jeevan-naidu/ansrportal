from django.contrib import admin
from .models import *
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.


class CommonAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ['created_by', 'updated_by']
        return super(CommonAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        else:
            obj.updated_by = request.user
        obj.save()

admin.site.register(TemplateMaster, CommonAdmin)
admin.site.register(TemplateProcessReview, CommonAdmin)
admin.site.register(DefectTypeMaster, CommonAdmin)
admin.site.register(SeverityLevelMaster, CommonAdmin)
admin.site.register(DefectClassificationMaster, CommonAdmin)
admin.site.register(ReviewMaster) #
admin.site.register(ReviewGroup) #
admin.site.register(WorkPacketMaster, CommonAdmin)
admin.site.register(DefectSeverityLevel, CommonAdmin)
admin.site.register(QASheetHeader, CommonAdmin)#
admin.site.register(ReviewReport, CommonAdmin)#
admin.site.register(QMSProcessModel, CommonAdmin)
admin.site.register(ProjectTemplateProcessModel, CommonAdmin)
admin.site.register(ComponentMaster, CommonAdmin)
admin.site.register(ChapterComponent, CommonAdmin)
admin.site.register(DSLTemplateReviewGroup, CommonAdmin)
