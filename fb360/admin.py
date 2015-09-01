from django.contrib import admin
from .models import Question, Answer, Feedback


class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'ans',
        )
    list_filter = ('ans',)
    ordering = ('ans', )


class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'qst',
        'category',
        )
    list_filter = ('qst',)
    ordering = ('qst', )


class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'qst',
        'year',
        'start_date', 'end_date',
        'selection_date', 'approval_date'
        )
    list_filter = ('qst', 'year', )
    ordering = ('year', )


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Feedback, FeedbackAdmin)
