from django.conf.urls import url
from views import MyProfileView
from django.contrib.auth.decorators import login_required
from UserProfile import views
urlpatterns = [
                       url(r'^$', login_required(MyProfileView.as_view()), name=u'myprofile'),
                       
                       ]