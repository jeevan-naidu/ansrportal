from django.conf.urls import patterns, url
from views import MilestoneReportsView
from django.contrib.auth.decorators import login_required
urlpatterns = patterns(u'',
                       url(r'^milestones/$', login_required(MilestoneReportsView.as_view()), name=u'milestone_reports'),
                       
                       )