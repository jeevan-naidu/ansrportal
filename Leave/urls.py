from django.conf.urls import patterns, url
from views import *
from django.contrib.auth.decorators import login_required
from Leave import views
urlpatterns = patterns(u'',
                       url(r'^$', login_required(Dashboard), name=u'Dashboard'),
                       url(r'^add/$', login_required(ApplyLeaveView.as_view()), name=u'leave_list'),
                       url(r'^cancel/$', login_required(LeaveCancel), name=u'leave_cancel'),
                       url(r'^details/$', login_required(LeaveDetails), name=u'leave_details'),
                       url(r'^transaction/$', login_required(LeaveTransaction), name=u'LeaveTransaction' )
                       )
