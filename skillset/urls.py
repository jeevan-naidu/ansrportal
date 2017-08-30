from django.conf.urls import url, include, patterns
from django.contrib.auth.decorators import login_required
from skillset import views

urlpatterns = [

    url(r'^$', login_required(views.SkillSet)),
    url(r'^skill_assign/$', login_required(views.SkillSet_assign)),
    url(r'^skill_detail/$', login_required(views.skill_detail)),
    url(r'^skill_add/$', login_required(views.skill_add)),
    url(r'^skill_delete/$', login_required(views.skill_delete)),
    ]