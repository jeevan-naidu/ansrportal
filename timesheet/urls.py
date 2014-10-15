from django.conf.urls import patterns, url
from timesheet import views

urlpatterns = patterns(u'',
                       url(r'^add$', views.Timesheet, name=u'timesheet'),
                       url(r'^project/add$',
                           views.CreateProjectWizard.as_view(views.FORMS),
                           name=u'createproject'),
                       url(r'^logout/$', views.Logout, name=u'logout'),
                       url(r'^$', views.index, name=u'index'),
                       )
