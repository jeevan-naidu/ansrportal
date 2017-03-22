from django.contrib import admin
from models import Skill_Lists, User_Skills

# Register your models here.

class SkillListsAdmin(admin.ModelAdmin):
    list_display = ['skill_name', 'level1', 'level2', 'level3']

class UserSkillsAdmin(admin.ModelAdmin):
	list_display = ['emp_mid', 'skills_name','skills_type']

admin.site.register(Skill_Lists, SkillListsAdmin)
admin.site.register(User_Skills, UserSkillsAdmin)