from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import *
from MyANSRSource.autocomplete_light_registry import *
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    url(r'^$', (login_required(AssessmentView.as_view())), name=u'qms'),
                       # url(r'^/edit(?P<pk>\d+)/$', login_required(AssessmentReviewEditView.as_view()), name=u'edit_review'),
    url(r'^edit/$', (ReviewReportManipulationView.as_view()), name='edit_review'),
                       # url(r'^$', login_required(AssessmentReviewCreateView.as_view()), name=u'create_review'),
                       url(r'^fetch_severity/$', fetch_severity, name=u'fetch_severity'),
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