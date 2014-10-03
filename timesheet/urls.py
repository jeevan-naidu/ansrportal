from django.conf.urls import patterns, url
from timesheet import views
from timesheet.forms import ProjectBasicInfoForm, ProjectTeamForm, \
    ProjectMilestoneForm

urlpatterns = patterns(u'',
                       url(r'^$', views.index, name=u'index'),
                       url(r'^createproject$',
                           views.CreateProject.as_view([
                               ProjectBasicInfoForm,
                               ProjectTeamForm,
                               ProjectMilestoneForm
                           ]),
                           name=u'createproject'),
                       url(r'^savenewproject$', views.process_form_data,
                           name=u'savenewproject'),
                       url(r'^logout/$', views.Logout, name=u'logout'),
                       )
