from django.conf.urls import patterns, url
from . import fbviews, choosepeerview, choosereporteeview, managerequest, \
    chooseaddmanagerview

urlpatterns = patterns(u'',
                       url(r'^choose-peer/$',
                           choosepeerview.WrappedChoosePeerView,
                           name=u'peerrequest'),
                       url(r'^choose-reportee/$',
                           choosereporteeview.WrappedChoosePeerView,
                           name=u'choosereportee'),
                       url(r'^choose-additional-manager/$',
                           chooseaddmanagerview.WrappedChooseAddManagerView,
                           name=u'choosereportee'),
                       url(r'^request-action/$',
                           managerequest.WrappedDecideOnRequestView,
                           name=u'requestaction'),
                       url(r'^give-feedback/$',
                           fbviews.WrappedGiveFeedbackView,
                           name=u'givefeedback'),
                       )
