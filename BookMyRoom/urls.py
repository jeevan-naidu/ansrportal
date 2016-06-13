from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from views import index
urlpatterns = patterns(u'',
                       url(r'^$', login_required(index), name=u''),

                       )
