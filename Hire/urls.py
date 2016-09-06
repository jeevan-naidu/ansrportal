from django.conf.urls import patterns, url
from views import *
from django.contrib.auth.decorators import login_required

urlpatterns = patterns(u'',
                       url(r'^$', login_required(Hire.as_view()), name=u'candidate_detail'),
                       url(r'^addmrf/$', login_required(MRF.as_view()), name=u'add_mrf'),
                       url(r'^designation/$', login_required(designation), name=u'designation'),
                       url(r'^specialization/$', login_required(specialization), name=u'specialization'),
                       )