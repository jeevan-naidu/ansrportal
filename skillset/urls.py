from django.conf.urls import url, include, patterns
from django.contrib.auth.decorators import login_required
from skillset import views

urlpatterns = [

    url(r'^$', views.SkillSet),
    url(r'^dept/$',views.dept),
    url(r'^designation/$', views.designation),
    url(r'^lists/$', views.lists),
	]