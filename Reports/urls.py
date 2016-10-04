from django.conf.urls import url
from views import MilestoneReportsView
from django.contrib.auth.decorators import login_required
from MyANSRSource.autocomplete_light_registry import AutocompleteProjects

urlpatterns = [
    url(
        r'^AutocompleteProjects/$',
        AutocompleteProjects.as_view(),
        name='AutocompleteProjects',
    ),
    url(r'^milestones/$', login_required(MilestoneReportsView.as_view()), name=u'milestone_reports'),

]
