from django.contrib import admin
from .models import Question, FB360
import employee


class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'qst',
        )
    list_filter = ('qst',)
    ordering = ('qst', )

    def get_form(self, request, obj=None, **kwargs):
        form = super(QuestionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields[
            'category'].queryset = employee.models.Designation.objects.filter(
                active=True
            )
        return form


class FB360Admin(admin.ModelAdmin):
    list_display = (
        'year', 'start_date', 'end_date', 'selection_date',
        'approval_date',
        )
    list_filter = ('year', )
    ordering = ('year', )


admin.site.register(Question, QuestionAdmin)
admin.site.register(FB360, FB360Admin)
