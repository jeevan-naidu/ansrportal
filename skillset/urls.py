from django.conf.urls import url, include, patterns
from django.contrib.auth.decorators import login_required
from skillset import views

urlpatterns = [

    url(r'^$', login_required(views.SkillSet)),
    ]