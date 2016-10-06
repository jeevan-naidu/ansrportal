from django.conf.urls import url
from views import *
from django.contrib.auth.decorators import login_required
from autocomplete_light_registry import AutoCompleteRequisitionSearch, AutocompleteUserHireSearch, AutoCompleteRequisitionSearchUser

urlpatterns = [
                       url(r'^$', login_required(Hire.as_view()), name=u'candidate_detail'),
                       url(r'^addmrf/$', login_required(MRFAdd.as_view()), name=u'add_mrf'),
                       url(r'^addnewmrf/$', login_required(NewMRFAdd.as_view()), name=u'add_new_mrf'),
                       url(r'^processupdate/$', login_required(ProcessUpdate.as_view()), name=u'processupdate'),
                       url(r'^candidatesearch/$', login_required(candidatesearch), name=u'search_candidate'),
                       url(r'^mrfsearch/$', login_required(mrfsearch), name=u'search_mrf'),
                       url(r'^designation/$', login_required(designation), name=u'designation'),
                       url(r'^specialization/$', login_required(specialization), name=u'specialization'),
                       url(r'^AutoCompleteRequisitionSearch/$', login_required(AutoCompleteRequisitionSearch.as_view()),
                           name=u'hire_requisition_search'),
                       url(r'^AutocompleteUserHireSearch/$', login_required(AutocompleteUserHireSearch.as_view()),
                           name=u'hire_user_search'),
                       url(r'^AutoCompleteRequisitionSearchUser/$', login_required(AutoCompleteRequisitionSearchUser.as_view()),
                           name=u'hire_requsition_based_on_user'),
                       ]