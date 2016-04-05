from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from GrievanceAdmin.views import GrievanceAdminListView, GrievanceAdminEditView

urlpatterns = patterns(u'',
                       url(r'^$', login_required(GrievanceAdminListView.as_view()), name=u'list_grievanceAdmin'),
                       url(r'^edit/(?P<id>[0-9]+)/$', login_required(GrievanceAdminEditView.as_view()), name=u'edit_grievanceAdmin'),
                       # url(r'^category/$', login_required(views.EscalateGrievanceView), name=u'add_grievanceCategory'),
                       # url(r'^rate_and_close/$', login_required(views.RateAndCloseView), name=u'rate_and_close'),
                       )
