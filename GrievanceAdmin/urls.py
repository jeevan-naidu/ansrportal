from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from GrievanceAdmin.views import GrievanceAdminListView, GrievanceAdminEditView
from GrievanceAdmin.autocomplete_light_registry import AutocompleteGrievanceAdmin
from MyANSRSource.autocomplete_light_registry import AutocompleteUser


urlpatterns = [
                       url(r'^$', login_required(GrievanceAdminListView.as_view()), name=u'list_grievanceAdmin'),
                       url(r'^edit/(?P<id>[0-9]+)/$', login_required(GrievanceAdminEditView.as_view()),
                           name=u'edit_grievanceAdmin'),
                       url(r'^AutocompleteUser/$',  login_required(AutocompleteUser.as_view()),
                           name=u'AutocompleteUserGA'),
                       url(r'^AutocompleteGrievanceAdmin/$',  login_required(AutocompleteGrievanceAdmin.as_view()),
                           name=u'AutocompleteGrievanceAdmin'),
                       ]
