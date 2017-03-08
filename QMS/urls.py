from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import *
from .autocomplete_light_registry import *
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', (AssessmentView.as_view()), name=u'qms'),
    # url(r'^/edit(?P<pk>\d+)/$', login_required(AssessmentReviewEditView.as_view()), name=u'edit_review'),
    url(r'^edit/$', (ReviewReportManipulationView.as_view()), name='edit_review'),
    url(r'^choose_tabs/$', (ChooseTabs.as_view()), name='choose_tabs'),
    url(r'^fetch_severity/$', fetch_severity, name=u'fetch_severity'),
    url(r'^fetch_author/$', fetch_author, name=u'fetch_author'),
    url(r'^chapter_summary/$', chapter_summary, name=u'chapter_summary'),
    url(r'^review_completed/$', review_completed, name=u'review_completed'),
    url(r'^get_template_process_review/$', get_template_process_review,
        name=u'get_template_process_review'),
    url(r'^AutocompleteProjects/$', AutocompleteProjects.as_view(), name='AutocompleteProjects', ),
    url(r'^AutocompleteUser/$', AutocompleteUser.as_view(), name='AutocompleteUser', ),
    url(r'^AutocompleteChapters/$', AutocompleteChapters.as_view(), name='AutocompleteChapters', ),
    url(r'^AutocompleteComponents/$', AutocompleteComponents.as_view(), name='AutocompleteComponents', ),
    url(r'^AutocompleteProcessModel/$', AutocompleteProcessModel.as_view(), name='AutocompleteProcessModel', ),
    url(r'^AutocompleteTemplates/$', AutocompleteTemplates.as_view(), name='AutocompleteTemplates', ),
    url(r'^AutocompleteReviewGroup/$', AutocompleteReviewGroup.as_view(), name='AutocompleteReviewGroup', ),
    url(r'^AutoCompleteAssignUserProjectSpecific/$', AutoCompleteAssignUserProjectSpecific.as_view(),
        name='AutoCompleteAssignUserProjectSpecific', ),
    url(r'^AutoCompleteChapterSpecificComponent/$', AutoCompleteChapterSpecificComponent.as_view(),
        name='AutoCompleteChapterSpecificComponent', ),
    url(r'^dashboard/$', (DashboardView.as_view()),  name='qms_dashboard'),# TemplateView.as_view(template_name='qms_dashboard.html')),

                       ]
