from django.conf.urls import patterns, url
from MyANSRSource import views, reportviews
from MyANSRSource.autocomplete_light_registry import AutocompleteProjects,AutocompleteBook,AutocompleteUser
from Reports import views as milestonreporteviews
from .views import ApproveTimesheetView
from django.contrib.auth.decorators import login_required, permission_required

urlpatterns = [
    url(
        r'^AutocompleteProjects/$',
        AutocompleteProjects.as_view(),
        name='AutocompleteProjects',
    ),
    url(
        r'^AutocompleteUser/$',
        AutocompleteUser.as_view(),
        name='AutocompleteUser',
    ),

    url(
        r'^AutocompleteBook/$',
        AutocompleteBook.as_view(),
        name='AutocompleteBook',
    ),
    url(r'^getchapters/(?P<projectid>[0-9]+)/$',
        views.GetChapters,
        name=u'getchapters'),
    url(r'^gettask/(?P<projectid>[0-9]+)/$',
        views.GetTasks,
        name=u'gettasks'),
    url(r'^remainder/delete/(?P<remid>[0-9]+)/$',
        views.DeleteRemainder,
        name=u'deleteremainder'),
    url(r'^getholidays/(?P<memberid>[0-9]+)/$',
        views.GetHolidays,
        name=u'getchapters'),
    url(r'^getprojecttype$',
        views.GetProjectType,
        name=u'getprojecttype'),
    url(r'^timesheet/entry$',
        views.Timesheet,
        name=u'timesheet'),

    url(r'^timesheet/approve$', permission_required('MyANSRSource.approve_timesheet')(ApproveTimesheetView.as_view()),
        name='approve_time_sheet'),
    url(r'^timesheet/approve/(?P<startdate>(\d+))/(?P<enddate>(\d+))/$',
        permission_required('MyANSRSource.approve_timesheet')
        (ApproveTimesheetView.as_view())),
    url(r'^timesheet/approve/(?P<week>[\w\-]+)/(?P<startdate>(\d+))/(?P<enddate>(\d+))/$',
        permission_required('MyANSRSource.approve_timesheet')
        (ApproveTimesheetView.as_view())),

    url(r'^timesheet/time_sheet_employee', permission_required('MyANSRSource.approve_timesheet')
        (views.time_sheet_employee)),
    url(r'^timesheet/send_reminder_mail', permission_required('MyANSRSource.approve_timesheet')
        (views.send_reminder_mail)),

    url(r'^dashboard$',
        views.Dashboard,
        name=u'dashboard'),
    url(r'^project/cancel$',
        views.deleteProject,
        name=u'deleteproject'),
    url(r'^project/save$',
        views.saveProject,
        name=u'saveproject'),
    url(r'^project/notify-team$',
        views.notify,
        name=u'notifyteam'),
    url(r'^project/add$',
        views.WrappedCreateProjectView,
        name=u'createproject'),
    url(r'^project/modify$',
        views.WrappedChangeProjectView,
        name=u'modifyproject'),
    url(r'^project/view-project$',
        views.ViewProject,
        name=u'viewproject'),
    url(r'^reports/single-member$',
        reportviews.SingleTeamMemberReport,
        name=u'memberreport'),
    url(r'^reports/member-perfomance$',
        reportviews.TeamMemberPerfomanceReport,
        name=u'memberperfomancereport'),
    url(r'^reports/single-project$',
        reportviews.SingleProjectReport,
        name=u'projectreport'),
    url(r'^reports/project-perfomance$',
        reportviews.ProjectPerfomanceReport,
        name=u'projectperfomancereport'),
    url(r'^reports/revenue-recognition$',
        reportviews.RevenueRecognitionReport,
        name=u'revenuerecognitionreport'),
    url(r'^project/manage-team$',
        views.WrappedManageTeamView,
        name=u'manageteam'),
    url(r'^project/manage-projectleader$',
        views.WrappedManageTeamLeaderView,
        name=u'manageleader'),
    url(r'^project/trackmilestone$',
        views.WrappedTrackMilestoneView,
        name=u'trackmilestone'),

    url(r'^logout/$', views.Logout, name=u'logout'),
    url(r'^$', views.index, name=u'index'),
]
