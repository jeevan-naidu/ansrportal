from django.conf.urls import patterns, url
from timesheet import views

urlpatterns = patterns(u'',
                       url(r'^entry$', views.Timesheet, name=u'timesheet'),
                       url(r'^approve$',
                           views.ApproveTimesheet,
                           name=u'approvetimesheet'),
                       url(r'^dashboard$',
                           views.Dashboard,
                           name=u'dashboard'),
                       url(r'^project/delete$',
                           views.deleteProject,
                           name=u'deleteproject'),
                       url(r'^project/save$',
                           views.saveProject,
                           name=u'saveproject'),
                       url(r'^project/add$',
                           views.CreateProjectWizard.as_view(views.FORMS),
                           name=u'createproject'),
                       url(r'^logout/$', views.Logout, name=u'logout'),
                       url(r'^$', views.index, name=u'index'),
                       )
