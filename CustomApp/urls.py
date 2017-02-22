from __future__ import unicode_literals
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from views import StartProcess, process, ProcessListView, ProcessUpdate, ApproveListView


urlpatterns = [
    url(r'^$', process, name='taskprocess'),
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
        r'^(?P<app_name>\w+)/update/(?P<pk>\d+|None)/$',
        login_required(ProcessUpdate.as_view()),
        name="update"
    ),
    url(
        r'^(?P<app_name>\w+)/approve/$',
        login_required(ApproveListView.as_view()),
        name="approve"
    )

]