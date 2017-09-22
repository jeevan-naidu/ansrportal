from django.conf.urls import patterns, url
from MyANSRSource import views, reportviews
from MyANSRSource.autocomplete_light_registry import AutocompleteProjects,AutocompleteBook,AutocompleteUser, \
    AutocompleteProjectAsset, AutocompleteDatapointName, AutocompletesubPracticeName, AutocompleteQualitySOP, \
    Autocompleteprojectscope, AutocompleteMilestonetype, Autocompleteprojecttemplate, AutocompleteRole
from .views import ApproveTimesheetView, getheadid, soplink, milestonename, NewCreatedProjectApproval, ActiveEmployees,\
    month_wise_active_employees, get_project_summary , ActiveProjects, ProjectChangeApproval, WrappedModifyProjectView
from django.contrib.auth.decorators import login_required, permission_required

urlpatterns = [
    url(r'^AutocompleteMilestonetype/$',
        AutocompleteMilestonetype.as_view(),
        name='AutocompleteMilestonetype'),
    url(r'^AutocompleteRole/$',
        AutocompleteRole.as_view(),
        name='AutocompleteRole'),
    url(
        r'^AutocompleteProjects/$',
        AutocompleteProjects.as_view(),
        name='AutocompleteProjects',
    ),
    url(
        r'^Autocompleteprojectscope/$',
        Autocompleteprojectscope.as_view(),
        name='Autocompleteprojectscope',
    ),
    url(r'Autocompleteprojecttemplate/$',
        Autocompleteprojecttemplate.as_view(),
        name='Autocompleteprojecttemplate'),
    url(r'^practicehead/$',
        login_required(getheadid),
        name='HeadId'),
    url(r'^milestonename/$',
        login_required(milestonename),
        name='milestonename',
        ),
    url(r'^soplink/$',
        login_required(soplink),
        name='SopLink'),
    url(
        r'^AutocompleteQualitySOP/$',
        AutocompleteQualitySOP.as_view(),
        name='AutocompleteQualitySOP'
    ),
    url(
        r'^AutocompletesubPracticeName/$',
        AutocompletesubPracticeName.as_view(),
        name='AutocompletesubPracticeName',
    ),
    url(
        r'^AutocompleteProjectAsset/$',
        AutocompleteProjectAsset.as_view(),
        name='AutocompleteProjectAsset'
    ),
    url(
        r'^AutocompleteDatapointName/$',
        AutocompleteDatapointName.as_view(),
        name='AutocompleteDatapointName'
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
    url(r'^get_internal$',
        views.is_internal,
        name=u'is_internal'),
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

    url(r'^timesheet/pm_view',login_required(views.pm_view),name=u'project_manager_view'),
    url(r'^timesheet/pm_details',login_required(views.pm_details),name=u'project_manager_details'),
    url(r'^timesheet/pm_view/(?P<startdate>(\d+))/(?P<enddate>(\d+))/$', login_required(views.pm_view)),
    url(r'^timesheet/pm_view/(?P<week>[\w\-]+)/(?P<startdate>(\d+))/(?P<enddate>(\d+))/$', login_required(views.pm_view)),

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
    url(r'^project/modifyproject$',
        login_required(views.WrappedModifyProjectView),
        name=u'changeproject'),
    url(r'^project/view-project$',
        views.ViewProject,
        name=u'viewproject'),
    url(r'^reports/single-member$',
        reportviews.SingleTeamMemberReport,
        name=u'memberreport'),
    url(r'^reports/member-perfomance$',
        reportviews.TeamMemberPerfomanceReport,
        name=u'memberperfomancereport'),
    url(r'^reports/revenue-recognition$',
        reportviews.RevenueRecogniation,
        name=u'RevenueRecogniation'),
    url(r'^reports/single-project$',
        reportviews.SingleProjectReport,
        name=u'projectreport'),
    url(r'^reports/project-perfomance$',
        reportviews.ProjectPerfomanceReport,
        name=u'projectperfomancereport'),
    url(r'^project/manage-team$',
        views.WrappedManageTeamView,
        name=u'manageteam'),
    url(r'^project/manage-projectleader$',
        views.WrappedManageTeamLeaderView,
        name=u'manageleader'),
    url(r'^project/trackmilestone$',
        views.WrappedTrackMilestoneView,
        name=u'trackmilestone'),
    url(r'^project/trackmilestone/delivery$',
        views.WrappedTrackMilestoneViewDelivery,
        name=u'trackmilestonedelivery'),
    url(r'^project/newcreatedprojectapproval/$',
        login_required(NewCreatedProjectApproval.as_view()),
        name='new_created_project_approval'),
    url(r'^project/projectchangeapproval/$',
        login_required(ProjectChangeApproval.as_view()),
        name='ProjectChangeApproval'),
    url(r'^project/projectdetail/$',
        login_required(views.project_detail),
        name='projectdetail'),
    url(r'^project/project_change_detail/$',
        login_required(views.project_change_detail),
        name='project_change_detail'),
    url(r'^logout/$', views.Logout, name=u'logout'),
    url(r'^$', views.index, name=u'index'),
    url(r'^active_employees$', login_required(ActiveEmployees.as_view()),
        name='active_employees'),
    url(r'^active_projects$', login_required(ActiveProjects.as_view()),
        name='active_projects'),
    url(r'^month_wise_active_employees', month_wise_active_employees),
    url(r'^get_project_summary/(?P<project_id>[0-9]+)/$',   views.get_project_summary, name=u'get_project_summary'),
]
