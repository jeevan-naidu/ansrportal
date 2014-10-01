from django.conf.urls import patterns, url
from timesheet import views

urlpatterns = patterns(u'',
                       url(r'^$', views.index, name=u'index'),
		       url(r'^createproject$', views.CreateProject, name=u'createproject'),
		       url(r'^logout/$', views.Logout, name=u'logout'),
                       )
