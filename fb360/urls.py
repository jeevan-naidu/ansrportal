from django.conf.urls import patterns, url
from . import fbviews, choosepeerview, choosereporteeview, managerequest

urlpatterns = patterns(u'',
                       url(r'^choose-peer/$',
                           choosepeerview.WrappedChoosePeerView,
                           name=u'peerrequest'),
                       url(r'^request-action/$',
                           managerequest.WrappedDecideOnRequestView,
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
