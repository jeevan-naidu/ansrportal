from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from GrievanceAdmin.views import GrievanceAdminListView, GrievanceAdminEditView

urlpatterns = patterns(u'',
                       url(r'^$', login_required(GrievanceAdminListView.as_view()), name=u'list_grievanceAdmin'),
                       url(r'^edit/(?P<id>[0-9]+)/$', login_required(GrievanceAdminEditView.as_view()), name=u'edit_grievanceAdmin'),
                       )
