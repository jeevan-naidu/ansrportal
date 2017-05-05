from django.conf.urls import patterns, url
from views import *
from django.contrib.auth.decorators import login_required
from TimeInOffice import views

urlpatterns = [

        url(r'^$', login_required(timein), name=u'timein'),
        url(r'^weekwisedata/$', login_required(weekwisedata), name=u'week_wise_data'),
        url(r'^monthwisedata/$', login_required(monthwisedata), name=u'month_wise_data'),

        ]