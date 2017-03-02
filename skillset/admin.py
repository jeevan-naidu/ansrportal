from django.contrib import admin
from models import Skill_Lists

# Register your models here.

class SkillListsAdmin(admin.ModelAdmin):
    list_display = ['skill_name', 'level1', 'level2', 'level3']

admin.site.register(Skill_Lists, SkillListsAdmin)