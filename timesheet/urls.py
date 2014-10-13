from django.conf.urls import patterns, url
from timesheet import views
from timesheet.forms import ProjectBasicInfoForm, ProjectTeamForm, \
    ProjectMilestoneForm

urlpatterns = patterns(u'',
                       url(r'^add$', views.Timesheet, name=u'timesheet'),
                       url(r'^project/add$',
                           views.CreateProject,
                           name=u'createproject'
                           ),
                       url(r'^logout/$', views.Logout, name=u'logout'),
                       url(r'^$', views.index, name=u'index'),
                       )
