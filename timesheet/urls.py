from django.conf.urls import patterns, url
from timesheet import views

urlpatterns = patterns(u'',
                       url(r'^$', views.index, name=u'index'),
                       url(r'^check$', views.checkUser, name=u'checkUser')
                       )
