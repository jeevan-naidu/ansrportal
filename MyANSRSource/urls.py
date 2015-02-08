from django.conf.urls import patterns, url
from MyANSRSource import views

urlpatterns = patterns(u'',
                       url(r'^getchapters/(?P<bookid>[0-9])/$',
                           views.GetChapters,
                           name=u'getchapters'),
                       url(r'^getprojecttype$',
                           views.GetProjectType,
                           name=u'getprojecttype'),
                       url(r'^timesheet/entry$',
                           views.Timesheet,
                           name=u'timesheet'),
                       url(r'^timesheet/approve$',
                           views.ApproveTimesheet,
                           name=u'approvetimesheet'),
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
                       url(r'^project/trackmilestone$',
                           views.WrappedTrackMilestoneView,
                           name=u'trackmilestone'),
                       url(r'^logout/$', views.Logout, name=u'logout'),
                       url(r'^$', views.index, name=u'index'),
                       )
