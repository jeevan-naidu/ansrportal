from django.contrib import admin
from .models import *
from MyANSRSource.models import ProjectSopTemplate, qualitysop
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


class TemplateMasterAdmin(CommonAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
            ProjectSopTemplate.objects.create(name=obj.name, actual_name=obj.actual_name, is_active=obj.is_active,
                                              created_by=request.user)

        else:
            obj.updated_by = request.user
            t_obj = TemplateMaster.objects.get(pk=obj.id)
            pst_obj = ProjectSopTemplate.objects.get(name__icontains=t_obj.name)
            pst_obj.name, pst_obj.actual_name, pst_obj.is_active = obj.name, obj.actual_name, obj.is_active
            pst_obj.save()
        obj.save()


class QMSProcessModelAdmin(CommonAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
            qualitysop.objects.create(name=obj.name, SOPlink=obj.SOPlink,
                                      created_by=request.user)
        else:
            obj.updated_by = request.user
            previous_name = QMSProcessModel.objects.get(pk=obj.id).name
            sop_obj = qualitysop.objects.get(name__icontains=previous_name)
            sop_obj.name, sop_obj.product_type, sop_obj.is_active, sop_obj.SOPlink = obj.name, obj.product_type, obj.is_active, obj.SOPlink
            sop_obj.save()
        obj.save()

admin.site.register(TemplateMaster, TemplateMasterAdmin)
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
admin.site.register(QMSProcessModel, QMSProcessModelAdmin)
admin.site.register(ProjectTemplateProcessModel, CommonAdmin)
admin.site.register(ComponentMaster, CommonAdmin)
admin.site.register(ChapterComponent, CommonAdmin)
admin.site.register(DSLTemplateReviewGroup, CommonAdmin)
