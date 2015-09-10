from django.conf.urls import patterns, url
import views

urlpatterns = patterns(u'',
                       url(r'^choose-peer/$',
                           views.PeerRequest,
                           name=u'peerrequest'),
                       url(r'^approve-peer/$',
                           views.PeerAccept,
                           name=u'peeraccept'),
                       )
