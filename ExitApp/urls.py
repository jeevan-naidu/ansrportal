from django.conf.urls import url
from views import ExitFormAdd, ResignationAcceptance, ClearanceFormView, ClearanceList, exit_note_update, revert_resignation, update_manager_concent, update_hr_concent
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
                           login_required(exit_note_update),
                           name='list'),
                       url(r'^revertresignation/$',
                           login_required(revert_resignation),
                           name='list'),
                       url(r'^update-manager-value/$',
                           login_required(update_manager_concent),
                           name="list"),
                       url(r'^update-hr-value/$',
                           login_required(update_hr_concent),
                           name="list"),

                       ]
