from django.conf.urls import url
from views import MilestoneReportsView
from django.contrib.auth.decorators import login_required
urlpatterns = [
                       url(r'^milestones/$', login_required(MilestoneReportsView.as_view()), name=u'milestone_reports'),
                       
                       ]
