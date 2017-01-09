from django.conf.urls import url
from views import ExitFormAdd, ResignationAcceptance, ClearanceFormView, ClearanceList, updateauthtable
from django.contrib.auth.decorators import login_required, user_passes_test
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
                       url(r'^clearance-list/$',
                           login_required(ClearanceList.as_view()),
                           name='list'),
                       url(r'^update-auth/$',
                           login_required(updateauthtable),
                           name='list'),

                       ]
