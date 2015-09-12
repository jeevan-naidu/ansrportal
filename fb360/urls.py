from django.conf.urls import patterns, url
import views, fbviews

urlpatterns = patterns(u'',
                       url(r'^choose-peer/$',
                           views.PeerRequest,
                           name=u'peerrequest'),
                       url(r'^request-action/$',
                           views.RequestAction,
                           name=u'requestaction'),
                       url(r'^choose-reportee/$',
                           views.ChooseReportee,
                           name=u'choosereportee'),
                       url(r'^feedback/$',
                           fbviews.MyFBRequestees,
                           name=u'MyFBRequestees'),
                       )
