from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import *
from MyANSRSource.autocomplete_light_registry import *

urlpatterns = [
                       url(r'^$', login_required(AssessmentView.as_view()), name=u''),
                       url(
                            r'^AutocompleteProjects/$',
                            AutocompleteProjects.as_view(),
                            name='AutocompleteProjects',
                        ),
                       url(
                            r'^AutocompleteUser/$',
                            AutocompleteUser.as_view(),
                            name='AutocompleteUser',
                        ),

                       url(
                            r'^AutocompleteChapters/$',
                            AutocompleteChapters.as_view(),
                            name='AutocompleteChapters',
                        ),
                       ]