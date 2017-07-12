from __future__ import unicode_literals
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from views import StartProcess,\
    ProcessListView,\
    ProcessApproval,\
    ApproveListView,\
    UpdateProcess,\
    GetProcess


urlpatterns = [
    url(
        r'^(?P<app_name>\w+)$',
        login_required(ProcessListView.as_view()),
        name="list_process"
    ),
    url(
        r'^(?P<app_name>\w+)/create/$',
        login_required(StartProcess.as_view()),
        name="create"
    ),
    url(
        r'^(?P<app_name>\w+)/approve/(?P<pk>\d+|None)/$',
        login_required(ProcessApproval.as_view()),
        name="approve"
    ),
    url(
        r'^(?P<app_name>\w+)/approve_list/$',
        login_required(ApproveListView.as_view()),
        name="approve_list"
    ),
    url(
        r'^(?P<app_name>\w+)/update/(?P<pk>\d+|None)/$',
        login_required(UpdateProcess.as_view()),
        name="update"
    ),
    url(
        r'^(?P<app_name>\w+)/get_process/(?P<pk>\d+|None)/$',
        login_required(GetProcess.as_view()),
        name="get_process"
    )

]