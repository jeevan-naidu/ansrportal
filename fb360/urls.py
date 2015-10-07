from django.conf.urls import patterns, url
from . import views, fbviews, choosepeerview, choosereporteeview

urlpatterns = patterns(u'',
                       url(r'^choose-peer/$',
                           choosepeerview.WrappedChoosePeerView,
                           name=u'peerrequest'),
                       url(r'^request-action/$',
                           views.RequestAction,
                           name=u'requestaction'),
                       url(r'^choose-reportee/$',
                           choosereporteeview.WrappedChoosePeerView,
                           name=u'choosereportee'),
                       url(r'^feedback/$',
                           fbviews.MyFBRequestees,
                           name=u'MyFBRequestees'),
                       url(r'^feedback/qa$',
                           fbviews.GetQA,
                           name=u'getqa'),
                       )
