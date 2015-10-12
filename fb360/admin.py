from .models import Question, FB360, Group
import employee
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple


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


class FB360Form(forms.ModelForm):

    class Meta:
        model = FB360
        exclude = None
        widgets = {'eligible': FilteredSelectMultiple("Person(s)", is_stacked=False)}


class FB360Admin(admin.ModelAdmin):

    form = FB360Form
    list_display = (
        'name', 'start_date', 'end_date', 'selection_date',
        'approval_date'
        )
    list_filter = ('name', )
    ordering = ('name', )


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_filter = ('name', )
    ordering = ('name', )

admin.site.register(Group, GroupAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(FB360, FB360Admin)
