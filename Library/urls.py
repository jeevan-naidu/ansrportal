from django.conf.urls import  url
from views import *
from django.contrib.auth.decorators import login_required
urlpatterns = [
                       url(r'^$', login_required(dashboard), name=u'Library_dashboard'),
                       url(r'^bookrent/$', login_required(bookrent), name=u'Library_bookrent'),
                       url(r'^adminaction/$', login_required(adminaction), name=u'Library_adminaction'),
                       url(r'^bookreturn/$', login_required(bookreturn), name=u'Library_bookreturn'),
                       url(r'^booksearch/$', login_required(booksearch), name=u'Library_booksearch'),
                       url(r'^booksearchpage/$', login_required(booksearchpage), name=u'Library_booksearchpage'),
                       url(r'^booksearchbyname/$', login_required(booksearchbyname), name=u'Library_booksearchpagename'),
                       url(r'^detail/$', login_required(bookdetail), name=u'Library_bookdetail'),
                       ]