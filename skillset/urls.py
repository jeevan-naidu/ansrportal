from django.conf.urls import url, include, patterns
from django.contrib.auth.decorators import login_required
from skillset import views
from skillset.autocomplete_light_registry import AutocompleteUserSearch

urlpatterns = [

    url(r'^$', login_required(views.SkillSet)),
    url(r'^dept/$', login_required(views.dept)),
    url(r'^user/$', login_required(views.user)),
    url(r'^skills/$', login_required(views.skills)),
    url(r'^filter1/$', login_required(views.filter1)),
    url(r'^AutocompleteUserSearch/$', login_required(AutocompleteUserSearch.as_view()),
        name=u'AutocompleteUserSearch'),
    url(r'^filters/$', login_required(views.filters)),
	]