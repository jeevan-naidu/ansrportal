from django.conf.urls import url, include, patterns
from django.contrib.auth.decorators import login_required
from views import *

urlpatterns = [
    url(r'^return/$', login_required(LaptopReturn.as_view()), name=u'employee'),
    # url(r'^return_apply/$', login_required(return_apply), name=u'return'),
    # url(r'^return_approve/$', login_required(return_approve), name=u'approve'),
]