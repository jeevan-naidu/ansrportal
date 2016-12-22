from django.conf.urls import url
from views import ExitFormAdd, ResignationAcceptance, ClearanceFormView
from django.contrib.auth.decorators import login_required
from autocomplete_light_registry import AutoCompleteRequisitionSearch, AutoCompleteResigneeSearch

urlpatterns = [
                       url(r'^exit-peer/$',
                           login_required(ExitFormAdd.as_view()),
                           name='exitrequest'),
                       url(r'^exit-acceptance/$',
                           login_required(ResignationAcceptance.as_view()),
                           name='exitacceptance'),
                       url(r'^clearance/$',
                           login_required(ClearanceFormView.as_view()),
                           name='clearance'),
                       url(r'^AutoCompleteRequisitionSearch/$',
                           login_required(AutoCompleteRequisitionSearch.as_view()),
                           name='resignee_search'),
                       url(r'^AutoCompleteResigneeSearch/$',
                           login_required(AutoCompleteResigneeSearch.as_view()),
                           name='resignee_filter'),

                       ]
