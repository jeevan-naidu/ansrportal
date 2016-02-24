from django.conf.urls import patterns, url
from views import GrievancesListView, AddGrievanceView
from django.contrib.auth.decorators import login_required
from Grievances import views
urlpatterns = patterns(u'',
                       url(r'^$', login_required(GrievancesListView.as_view()), name=u'list_grievance'),
                       url(r'^add/$', login_required(AddGrievanceView.as_view()), name=u'add_grievance'),
                       url(r'^escalate/$', login_required(views.EscalateGrievanceView), name=u'escalate_grievance'),
                       url(r'^rate_and_close/$', login_required(views.RateAndCloseView), name=u'rate_and_close'),
                       
                       )