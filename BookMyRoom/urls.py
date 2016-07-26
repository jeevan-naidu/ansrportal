from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from BookMyRoom.views import BookMeetingRoomView, GetBookingsView, CancelBooking, GetAllRoomsList, GetBookingDetails

urlpatterns = patterns(u'',
                       url(r'^$', login_required(BookMeetingRoomView.as_view()), name=u''),
                       url(r'^details/$', login_required(GetBookingsView), name=u''),
                       url(r'^cancel/$', login_required(CancelBooking), name=u''),

                       # Urls for android app
                       url(r'^get-bookings-details/$', GetBookingDetails, name=u''),
                       url(r'^get-all-rooms/$', GetAllRoomsList, name=u''),
                       )
