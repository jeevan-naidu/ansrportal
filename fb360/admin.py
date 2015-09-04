from django.contrib import admin
from django import forms
from .models import Question, Answer, Feedback


class AnswerInlineFormSet(forms.ModelForm):

    class Meta:
        widgets = {
            'ans': forms.TextInput(
                attrs={
                    'style': 'width:1024px',
                    })
        }


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    exclude = []
    form = AnswerInlineFormSet


class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'qst',
        'category',
        )
    list_filter = ('qst',)
    ordering = ('qst', )
    inlines = [AnswerInline, ]


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
admin.site.register(Feedback, FeedbackAdmin)
