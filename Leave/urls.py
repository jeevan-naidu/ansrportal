from django.conf.urls import patterns, url
from views import *
from django.contrib.auth.decorators import login_required
from Leave import views
from Leave.autocomplete_light_registry import AutocompleteUserSearch

urlpatterns = [
                       url(r'^$', login_required(Dashboard.as_view()), name=u'Leave_dashboard'),
                       url(r'^add/$', login_required(ApplyLeaveView.as_view()), name=u'leave_list'),
                       url(r'^cancel/$', login_required(LeaveCancel), name=u'leave_cancel'),
                       url(r'^details/$', login_required(LeaveDetails), name=u'leave_details'),
                       url(r'^transaction/$', login_required(LeaveTransaction), name=u'LeaveTransaction'),
                       url(r'^leavelist/$', login_required(LeaveListView.as_view()), name=u'list_leave'),
                       url(r'^leavelist/(?P<all>[a-z]+)/$', login_required(LeaveListView.as_view()),
                           name=u'list_leave_all'),
                       url(r'^manage/$', login_required(LeaveManageView.as_view(template_name='Manager.html')),
                           name=u'manage_leave_list'),
                       url(r'^manage/(?P<all>[a-z]+)/$', login_required(LeaveManageView.as_view()),
                           name=u'list_leave_all'),
                       url(r'^ShortAttendanceTransact/$', login_required(ShortAttendanceTransact),
                           name=u'ShortAttendanceTransact'),
                       url(r'^ShortAttendanceDetail/$', login_required(ShortAttendanceDetail),
                           name=u"ShortAttendanceDetail"),
                       url(r'^shortleavemanage/$',
                           login_required(ShortAttendanceManageView.as_view()),
                           name=u'Short_Attendance_Manage_View'),
                       url(r'^addshortleave/$',
                           login_required(ApplyShortLeaveView.as_view()),
                           name=u'short_leave_list'),
                       url(r'^raisedispute/$', login_required(RaiseDispute.as_view()), name=u'raise_dispute'),
                       url(r'^AutocompleteUserSearch/$', login_required(AutocompleteUserSearch.as_view()),
                           name=u'AutocompleteUserSearch'),
                       url(r'^report/$', login_required(report), name=u'leave_report'),
                       url(r'^monthwisedata/$', login_required(monthwisedata), name=u'month_wise_data'),
                       url(r'^weekwisedata/$', login_required(weekwisedata), name=u'week_wise_data'),
                       url(r'^admincancel/$', login_required(adminleavecancel), name=u'admin_leave_cancel'),
                       url(r'^balance_based_on_year/$',
                           login_required(balance_based_on_year),
                           name=u'balanced_based_on_year')

                       ]
