from django.conf.urls import  url
from django.contrib.auth.decorators import login_required
from BookMyRoom.views import BookMeetingRoomView, GetBookingsView, CancelBooking

urlpatterns = [
                       url(r'^$', login_required(BookMeetingRoomView.as_view()), name=u''),
                       url(r'^details/$', login_required(GetBookingsView), name=u''),
                       url(r'^cancel/$', login_required(CancelBooking), name=u''),

                       ]
