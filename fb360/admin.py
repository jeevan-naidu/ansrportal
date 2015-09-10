from django.contrib import admin
from .models import Question, FB360


class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'qst',
        )
    list_filter = ('qst',)
    ordering = ('qst', )


class FB360Admin(admin.ModelAdmin):
    list_display = (
        'year', 'selection_start_date',
        'start_date', 'end_date',
        'selection_date', 'approval_date'
        )
    list_filter = ('year', )
    ordering = ('year', )


admin.site.register(Question, QuestionAdmin)
admin.site.register(FB360, FB360Admin)
