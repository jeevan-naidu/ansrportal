from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import *
from .autocomplete_light_registry import *
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    url(r'^$', (login_required(AssessmentView.as_view())), name=u'qms'),
    # url(r'^/edit(?P<pk>\d+)/$', login_required(AssessmentReviewEditView.as_view()), name=u'edit_review'),
    url(r'^edit/$', (ReviewReportManipulationView.as_view()), name='edit_review'),
    url(r'^choose_tabs/$', login_required((ChooseTabs.as_view())), name='choose_tabs'),
                       # url(r'^$', login_required(AssessmentReviewCreateView.as_view()), name=u'create_review'),
    url(r'^fetch_severity/$', fetch_severity, name=u'fetch_severity'),
    url(r'^fetch_author/$', fetch_author, name=u'fetch_author'),
    url(r'^get_template_process_review/$', get_template_process_review,
        name=u'get_template_process_review'),
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
    url(
        r'^AutocompleteComponents/$',
        AutocompleteComponents.as_view(),
        name='AutocompleteComponents',
    ),

    url(
        r'^AutocompleteProcessModel/$',
        AutocompleteProcessModel.as_view(),
        name='AutocompleteProcessModel',
    ),
    url(
        r'^AutocompleteTemplates/$',
        AutocompleteTemplates.as_view(),
        name='AutocompleteTemplates',
    ),

    url(
        r'^AutocompleteReviewGroup/$',
        AutocompleteReviewGroup.as_view(),
        name='AutocompleteReviewGroup',
    ),
    url(
        r'^AutoCompleteAssignUserProjectSpecific/$',
        AutoCompleteAssignUserProjectSpecific.as_view(),
        name='AutoCompleteAssignUserProjectSpecific',
    ),

                       ]
