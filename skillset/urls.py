from django.conf.urls import url, include, patterns
from django.contrib.auth.decorators import login_required
from skillset import views
from skillset.autocomplete_light_registry import AutocompleteUserSearch

urlpatterns = [

    url(r'^$', views.SkillSet),
    url(r'^dept/$',views.dept),
    url(r'^designation/$', views.designation),
    url(r'^AutocompleteUserSearch/$', login_required(AutocompleteUserSearch.as_view()),
        name=u'AutocompleteUserSearch'),
    url(r'^lists/$', views.lists),
	]