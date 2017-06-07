from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import *
from .autocomplete_light_registry import *
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', login_required(AssessmentView.as_view()), name=u'qms'),
    url(r'^review/(?P<id>\d+)/(?P<chapter_component_id>\d+)/(?P<review_group_id>\d+)/$',
        login_required(ReviewRedirectView.as_view()), name= u'review_redirect_view'),

    url(r'^edit/$', login_required(ReviewReportManipulationView.as_view()), name='edit_review'),
    url(r'^choose_tabs/$', login_required(ChooseTabs.as_view()), name='choose_tabs'),
    url(r'^fetch_severity/$', login_required(fetch_severity), name=u'fetch_severity'),
    url(r'^fetch_author/$', login_required(fetch_author), name=u'fetch_author'),
    url(r'^chapter_summary/$', login_required(chapter_summary), name=u'chapter_summary'),
    url(r'^review_completed/$', login_required(review_completed), name=u'review_completed'),
    url(r'^mark_as_completed/$', login_required(mark_as_completed), name=u'tab_review_completed'),
    url(r'^get_template_process_review/$', login_required(get_template_process_review),
        name=u'get_template_process_review'),
    url(r'^AutocompleteProjects/$', login_required(AutocompleteProjects.as_view()), name='AutocompleteProjects', ),
    url(r'^AutocompleteUser/$', login_required(AutocompleteUser.as_view()), name='AutocompleteUser', ),
    url(r'^AutocompleteChapters/$', login_required(AutocompleteChapters.as_view()), name='AutocompleteChapters', ),
    url(r'^AutocompleteComponents/$', login_required(AutocompleteComponents.as_view()), name='AutocompleteComponents', ),
    url(r'^AutocompleteProcessModel/$', login_required(AutocompleteProcessModel.as_view()), name='AutocompleteProcessModel', ),
    url(r'^AutocompleteTemplates/$', login_required(AutocompleteTemplates.as_view()), name='AutocompleteTemplates', ),
    url(r'^AutocompleteReviewGroup/$', login_required(AutocompleteReviewGroup.as_view()), name='AutocompleteReviewGroup', ),
    url(r'^AutoCompleteUserProjectSpecific/$', login_required(AutoCompleteUserProjectSpecific.as_view()), name='AutoCompleteUserProjectSpecific', ),
    url(r'^AutoCompleteAssignUserProjectSpecific/$', login_required(AutoCompleteAssignUserProjectSpecific.as_view()),
        name='AutoCompleteAssignUserProjectSpecific', ),
    url(r'^AutoCompleteChapterSpecificComponent/$', login_required(AutoCompleteChapterSpecificComponent.as_view()),
        name='AutoCompleteChapterSpecificComponent', ),
    url(r'^dashboard/$', login_required(DashboardView.as_view()),  name='qms_dashboard'),# TemplateView.as_view(template_name='qms_dashboard.html')),
    url(r'^review_list/$', login_required(ReviewListView.as_view()), name='review_list'),
    url(r'^export_review/$', login_required(ExportReview.as_view()), name='export_review'),
                       ]
