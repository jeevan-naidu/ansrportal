from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from views import index, GetBookingsView
urlpatterns = patterns(u'',
                       url(r'^$', login_required(index), name=u''),
                       url(r'^details/$', login_required(GetBookingsView), name=u''),

                       )
